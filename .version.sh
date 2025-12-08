# .version.h
# Copyright (c) 2021 Centre National d'Etudes Spatiales (CNES).
#
# This file is part of CODIP
#
#     https://gitlab.cnes.fr/co3d-image/codip
# This script returns the current version number of a repository
# depending on the state of the repository.
#
# WARNING : do not edit unless critical failure.
#

# handle override variable
if [ -n "$CODIP_FORCE_VERSION" ]; then
  echo "$CODIP_FORCE_VERSION"
  exit 0
fi

version=`git tag --points-at HEAD | tail -n 1`".0"
git diff --quiet
diff=$?

# Version is a release candidate for next number if:
# - we are not on a tag
# - we are not on master
# - we have made some changes in the current repository
if [ "$version" = ".0" ] || [ $diff -eq 1 ]; then
    v=`git describe --tags --abbrev=0 2>/dev/null`
    if [ "$v" = "" ]; then
        # when no version number is found on this branch, use the current version in sources
        v=$(grep '^project' CMakeLists.txt | sed -E 's/.*VERSION ([a-zA-Z0-9\.-]+).*/\1/')
    fi
    # Check if we are on master
    cur_branch=`git rev-parse --abbrev-ref HEAD`
    if [ "$cur_branch" = "HEAD" ]; then
        cur_branch="$BRANCH_NAME"
    fi
    # when "reset" is given as an argument, the version will be the latest tag
    if [ "$1" = "reset" ]; then
        version=$v
    elif [ "$cur_branch" = "master" ] && [ $diff -eq 0 ]; then
        # on a clean master: use last tag + number of commits ahead
        commits_ahead=`git describe --tags | cut -d '-' -f 2`
        version=${v}.${commits_ahead}
    else
        version=${v%.*}.$((${v##*.}+1))-rc
    fi
fi

echo $version
