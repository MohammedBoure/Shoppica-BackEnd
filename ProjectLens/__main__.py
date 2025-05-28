import sys
import os

# Add the ProjectLens package directory to sys.path
package_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, package_dir)

from main import main

if __name__ == "__main__":
    main()