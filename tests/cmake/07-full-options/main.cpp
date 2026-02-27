// Note the custom include path from INCLUDE_PREFIX
#include "my-includes/foo/bar/version.hpp"
#include <iostream>

int main() {
    // Note the custom namespace
    std::cout << "Version: " << foo::bar::VERSION << std::endl;
    return 0;
}
