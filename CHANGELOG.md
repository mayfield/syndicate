# Change Log


## [Unreleased] - unreleased

## [1.3.0] - 2015-10-19
### Added
- Adapter.{set_cookie, get_cookie and get_header} methods for consistent
  cookie interfaces regardless of adapter type.


## [1.2.0] - 2015-09-10
### Added
- Support for per request timeouts via {get,post,put,...}(..., timeout=10)


## [1.1.0] - 2015-09-09
### Changed
- xml serializer support
- multi header support of HeaderAuth
- Service(trailing_slash=True) will always append a slash

### Fixed
- urn-less support for APIs that don't have a fixed urn


## [1.0.0] - 2014-01-25
### Changed
- First stable release


[unreleased]: https://github.com/mayfield/syndicate/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/mayfield/syndicate/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/mayfield/syndicate/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/mayfield/syndicate/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/mayfield/syndicate/compare/b9ec552eb9967c5622053c33b0b0a4789a16ffab...v1.0.0
