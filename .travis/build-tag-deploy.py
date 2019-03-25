#!/usr/bin/env python
# coding=utf-8

import os

import re

import docker
import git
from packaging import specifiers, version

ENV_DEFAULT = '-'
VERSION_SPLIT_PATTERN = re.compile(r'([!~<>=]+)')


def handle_docker_client_stream(decoded_generator, _print=True, debug=False):
    """Parse the message stream from the Docker daemon.

    The Docker API returns a stream of JSON (parsed) dicts that contain the
    messages for the given docker command. The dict is parsed here and the
    message is printed as it would be if the docker command is called from the
    command line. Any relevant information (image hashes, push results) as
    parsed and returned as needed.
    """
    image_id = None
    tag_info = None

    for data in decoded_generator:
        for key in ['stream', 'status', 'aux', 'error']:
            if key in data:
                break

        if (key == 'error'):
            raise Exception(data[key])
        elif (key == 'aux'):
            if 'ID' in data[key]:
                image_id = data[key]['ID']
            elif 'Tag' in data[key]:
                tag_info = data[key]
            # Add newline for pretty printing
            data[key] = '{}\n'.format(data[key])

        if debug:
            print data
        if _print:
            print data[key],

    if image_id:
        return image_id
    if tag_info:
        return tag_info


def generate_tags(sopel_branch_tag, current_python_tag, default_python_tag):
    """Generate a list of tags to identify the specified image.

    If the current python version matches the default python tag (which may not
    be the latest python built), then a python-less (and python-short; e.g., 3
    vs. 3.6) specifier is also generated (i.e., it only has the Sopel version in
    the tag.)

    Returns: str: tag for image like '6.5.3-py3.5'

        - A python-less tag like: '6.5.3'
        - The following tags are equivalent (assuming latest Sopel version)
            - '6.5.3-py3.6'
            - '6.5-py3.6'
            - '6-py3.6'
            Assuming DEFAULT_PYTHON_TAG=3.6-alpine
            - '6.5.3-py3'
            - '6.5.3'
            - '6.5-py3'
            - '6.5'
            - '6-py3'
            - '6'
    """
    sopel_version = version.parse(sopel_branch_tag[1:])
    current_python_version = version.parse(current_python_tag.split('-')[0])
    tags = []

    sopel_version_parts = map(str, sopel_version.release)
    current_python_parts = map(str, current_python_version.release)

    start_pv = 0 if (current_python_tag == default_python_tag) or (
        current_python_version.release[0] == 2) else 1
    for sv in range(3):
        for pv in range(start_pv, 2):
            tag = '{}-py{}'.format(
                '.'.join(sopel_version_parts[:sv + 1]), '.'.join(current_python_parts[:pv + 1]))
            tags.append(tag)
        if current_python_tag == default_python_tag:
            tag = '.'.join(sopel_version_parts[:sv + 1])
            tags.append(tag)

    return tags


def build(sopel_branch, sopel_branch_commit_hash, dockerfile_folder, base_build_args, docker_client):
    build_args = base_build_args.copy()
    build_args['SOPEL_BRANCH'] = sopel_branch
    build_args['VCS_REF'] = sopel_branch_commit_hash

    print 'BUILDING: {}\t{}'.format(build_args['PYTHON_TAG'], sopel_branch)
    decoded = docker_client.build(
        path=dockerfile_folder,
        pull=True,
        buildargs=build_args,
        decode=True,
    )

    return handle_docker_client_stream(decoded)


def tag(image_id, repository, tag, docker_client):
    print 'TAGGING: {}\t{}'.format(image_id, tag)
    return docker_client.tag(
        image=image_id,
        repository=repository,
        tag=tag
    )


def push(repository, tag, docker_client):
    print 'PUSHING: {}:{:<15s}'.format(repository, tag),
    decoded = docker_client.push(
        repository=repository,
        tag=tag,
        stream=True,
        decode=True
    )

    tag_info = handle_docker_client_stream(decoded, _print=False)
    print 'OK {:>10}\t{}'.format(
        tag_info['Size'],
        tag_info['Digest'],
    )


def parse_version_map(fp):
    """Parse file with Sopel version and (optional) minimum python version

    Expected format of version map file:
    ```
    # Everything after '#' is considered a comment
    v6.5.3  # Note leading 'v' (should match Sopel tags)
    v6.6.0>=3.7  # Sets minimum python requirement
    v6.6.1  # Will require Python >=3.7 because of previous line
    v6.6.2>3.5,<3.7  # Resets the minimum requirement flag
    v6.6.3  # Will require Python >3.5 and <3.7 (same as previous line)
    ```

    Args:
        fn (str): path for version map file

    Returns:
        list: tuples like (sopel_branch, required_python)

        - sopel_branch is the string (with leading 'v').
        - required_python is a parsed `packaging.specifiers.SpecifierSet`
          object if provided, else `None`.
    """
    to_build = []

    required_python = None
    with open(fp) as fh:
        for line in fh:
            if line.startswith('#'):  # Skip comments
                continue

            clean = line.strip().split('#', 1)[0].strip()
            if clean == '':
                continue

            splits = VERSION_SPLIT_PATTERN.split(clean, 1)
            sopel_branch = splits[0]
            if len(splits) > 1:
                required_python = specifiers.SpecifierSet(''.join(splits[1:]))

            to_build.append((sopel_branch, required_python))

    return to_build


def main(context):
    """Iterate over all Sopel versions, build, tag, and push.
    """

    # Get docker client
    d = docker.APIClient(base_url='unix://var/run/docker.sock')

    # Get Sopel tag commit hashes
    g = git.cmd.Git()
    remote_refs = {}
    for ref in g.ls_remote('https://github.com/sopel-irc/sopel.git').split('\n'):
        hash_ref_list = ref.split('\t')
        remote_refs[hash_ref_list[1]] = hash_ref_list[0]

    to_build = parse_version_map(context['VERSION-MAP_FILE'])
    python_tag = context['BASE_BUILD_ARGS']['PYTHON_TAG']
    current_python = version.parse(python_tag.split('-')[0])

    # Build and tag images
    tagged_images = set()
    for sopel_branch, required_python in to_build:
        if not required_python or (required_python and current_python in required_python):
            # Build
            image_id = build(
                sopel_branch,
                dockerfile_folder=context['DOCKERFILE_FOLDER'],
                base_build_args=context['BASE_BUILD_ARGS'],
                sopel_branch_commit_hash=remote_refs['refs/tags/{}'.format(
                    sopel_branch)],
                docker_client=d,
            )

            # Generate tags
            tags = generate_tags(
                sopel_branch,
                current_python_tag=python_tag,
                default_python_tag=context['DEFAULT_PYTHON_TAG'],
            )

            # Tag
            for t in tags:
                res = tag(
                    image_id,
                    repository=context['REGISTRY_REPO'],
                    tag=t,
                    docker_client=d
                )
                if res:
                    tagged_images.add(t)
        else:
            print 'SKIPPING: {}\t{}; Python {} required'.format(
                python_tag, sopel_branch, required_python)

    # Push tagged images. Do this last and all at once so images with overwritten
    # tags do not get push unnecessarily.
    if os.environ.get('TRAVIS_PULL_REQUEST') != 'false':
        return  # Do not push images for PR builds.

    d.login(
        username=context['REGISTRY_USER'],
        password=context['REGISTRY_PASS'],
    )
    for ti in tagged_images:
        push(
            repository=context['REGISTRY_REPO'],
            tag=ti,
            docker_client=d
        )


if __name__ == '__main__':
    context = {
        # Registry information
        'REGISTRY_REPO': os.environ.get('REGISTRY_REPO', ENV_DEFAULT),
        'REGISTRY_USER': os.environ.get('REGISTRY_USER', ENV_DEFAULT),
        'REGISTRY_PASS': os.environ.get('REGISTRY_PASS', ENV_DEFAULT),
        # build-args
        'BASE_BUILD_ARGS': {
            # Image labels
            'BUILD_DATE': os.environ.get('BUILD_DATE', ENV_DEFAULT),
            # 'VCS_REF': None,  ## Get for each Sopel version
            'DOCKERFILE_VCS_REF': os.environ.get('VCS_REF', ENV_DEFAULT),
            # Image versions
            'PYTHON_TAG': os.environ.get('PYTHON_TAG', ENV_DEFAULT),
            # 'SOPEL_BRANCH': None,  ## Iterate over each Sopel version
        },
        # Misc.
        'DEFAULT_PYTHON_TAG': os.environ.get('DEFAULT_PYTHON_TAG', ENV_DEFAULT),
        # Assumes the script is run from the base folder
        'DOCKERFILE_FOLDER': os.environ.get('DOCKERFILE_FOLDER', os.getcwd()),
        'VERSION-MAP_FILE': os.environ.get('VERSION-MAP_FILE', os.path.join(os.getcwd(), 'version-map.txt'))
    }

    main(context)
