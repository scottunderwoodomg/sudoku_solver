#!/bin/zsh

setupVirtualEnv() {
    # setup virtualenv, install requirements
    if  [[ $(uname -s) == Darwin* ]]
    then
        echo "running on mac"
        setupVirtualEnvMac
    else
        echo "Quitting - Unsupported platform!"
        exit 1
    fi
}

setupVirtualEnvMac() {
    rm -r ./venv       # force clean before setup (force remove throwing errors on mac)
    venvexec=`which virtualenv`
    syspy3="/usr/bin/python3"

    activateVenv
    pipInstallRequirements

    sudo chown -R venv #root argument skipped on mac setup
}

activateVenv() {
    echo "$venvexec, $syspy3"

    $syspy3 -m venv venv
    source venv/bin/activate
}

pipInstallRequirements() {
    sudo -H venv/bin/pip install --upgrade pip setuptools && venv/bin/pip install -r requirements.txt
}

main() {
    setupVirtualEnv
    if [ $setup_type != "all" ]
    then
        echo "Virtual-env setup done."
        exit 0
    fi

    echo "setup Done."
}

main "$*"
