# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [2021.3.0]

### Fixed
- add bsc203 entry point

## [2021.2.0]

### Added
- bsc203 support
- new config, behavior: "polling status"
- hardware support documentation in avprs

### Fixed
- added forgotten config options to is-daemon: enable, log_level, and log_to_file

## [2020.12.0]

### Added
- conda-forge as installation source

### Fixed
- Read units from config

## [2020.11.1]

### Changed
- Update position during motion

## [2020.11.0]

### Fixed
- entry point for KST101 fixed
- entry point "BSC201" was misspelled as "BSC101", fixed
- homing more reliable

### Changed
- regenerated avpr based on recent traits update
- use new trait base classes

## [2020.07.0]

### Changed
- Now uses Avro-RPC [YEP-107](https://yeps.yaq.fyi/107/)
- Uses Flit for distribution

## 2020.06.0

### Added
- initial release

[Unreleased]: https://gitlab.com/yaq/yaqd-thorlabs/-/compare/v2021.3.0...master
[2021.3.0]: https://gitlab.com/yaq/yaqd-thorlabs/-/compare/v2021.2.0...v2021.3.0
[2021.2.0]: https://gitlab.com/yaq/yaqd-thorlabs/-/compare/v2020.12.0...v2021.2.0
[2020.12.0]: https://gitlab.com/yaq/yaqd-thorlabs/-/compare/v2020.11.1...v2020.12.0
[2020.11.1]: https://gitlab.com/yaq/yaqd-thorlabs/-/compare/v2020.11.0...v2020.11.1
[2020.11.0]: https://gitlab.com/yaq/yaqd-thorlabs/-/compare/v2020.07.0...v2020.11.0
[2020.07.0]: https://gitlab.com/yaq/yaqd-thorlabs/-/compare/v2020.06.0...v2020.07.0
