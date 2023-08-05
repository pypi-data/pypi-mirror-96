# coverage_shield

Uploads total coverage to badges service.

## Usage
Just issue

    python3 -m coverage_shield

to upload coverage to the badges service. `coverage_shield` will try to autodetect the repo slug (e.g. "user/repo") by first looking at the origin remote of the current git repo, and also using environment variables if run on Travis CI.

## Author
Samuel Carlsson
