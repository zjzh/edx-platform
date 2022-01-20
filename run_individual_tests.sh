
if [[ $# -eq 0 ]] ; then
    echo 'Kindly provide path'
    exit 0
fi

test_files=()
failed_files=()

clear

for arg; do
    echo "Collecting directories from $arg"

    for file in $(find $arg -name 'test_*.py' -or -name 'tests_*.py' -or -name '*_tests.py' -or -name 'tests.py' -or -type f -path "*/tests/__init__.py") ; do
        test_files+=("$file")
    done
done

echo "Running pytest file-wise on all these files"
printf "\t%s\n" "${test_files[@]}"

for file in "${test_files[@]}" ; do
     python -Wd -m pytest --ds="$DJANGO_SETTINGS" -p no:warnings "$file"
    exit_code=$?
    if [ $exit_code -ne 0 ] && [ $exit_code -ne 5 ]
    then
        failed_files+=("$file")
    fi
done

if (( ${#failed_files[@]} != 0 )); then
    echo "Following files failed during run"
    printf "\t%s\n" "${failed_files[@]}"
    exit 1
fi
