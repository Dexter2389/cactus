BRANCH=`git rev-parse --abbrev-ref HEAD`

if [[ $BRANCH =~ (master|main|develop) ]]; then
    echo "You are on branch $BRANCH. Are you sure you want to commit to this branch?"
    echo "If so, commit with -n to bypass this pre-commit hook."
    exit 1
fi

exit 0