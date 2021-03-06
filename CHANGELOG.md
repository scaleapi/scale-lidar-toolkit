# Changelog

All notable changes to packages scale-lidar-io-debug and scale-lidar-io will be documented in this file.

## [0.1.14] - 2021-06-17

### Fixed

- Support Scale File Upload (alternative to S3)

## [0.1.13] - 2021-04-28

### Fixed

- Support Scale SDK +2.0

## [0.1.12] - 2021-03-08

### Fixed

- LidarImage calibrate issue

## [0.1.1] - 2021-03-05

### Fixed

- LidarImage save issue

## [0.1.1] - 2021-03-02

### Fixed

- k3-k6 distortion values issue

### Added

- Better comment on the code
- Handle better distortion values + set default to [k1,k2,p1,p2,k3,k4]
- Update example to use json instead of yaml

## [0.1.0] - 2021-02-04

### Added

- Add support for frame radar points (add_radar_point).
- Add support for frame points colors (add_colors).
