# resolves APT crashes due to Python issues
cd /usr/lib/python3/dist-packages
if [ ! -f apt_pkg.so ]; then
    file=$(ls apt_pkg.cpython-*-linux-gnu.so 2>/dev/null | head -n 1)
    if [ -n "$file" ]; then
        sudo cp "$file" apt_pkg.so
    else
        echo "No matching apt_pkg.cpython-*.so file found. Might be causing APT issues in the next steps."
    fi
fi
cd -