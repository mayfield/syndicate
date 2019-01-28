# Change Log

## [2.3] - 2018-01-28
### Fixed
- Python 3.7 support

### Changed
- Renamed adapaters to their implementation counter part. E.g. sync -> requests, ...


## [2.1.2] - 2016-11-05
### Fixed
- Fix for query args in new version of yarl (from aiohttp).


## [2.1.1] - 2016-11-03
### Fixed
- Updated cookie handling for new versions of aiohttp.


## [2.1] - 2015-12-04
### Added
- `Service.close` method for freeing resources.


## [2] - 2015-11-15
### Changed
- Replace tornado backend with asyncio/aiohttp.
- Python 3.4+ is required now. (soon to be 3.5!)


## [1.4.0] - 2015-10-24
### Changed
- The sync `get_pager` returns a sized iterator.
- Connect and request timeout can be set from Service init.

### Added
- Made it possible to pass configuration to Adapter construction.


## [1.3.0] - 2015-10-19
### Added
- `Adapter.{set_cookie, get_cookie and get_header}` methods for consistent
  cookie interfaces regardless of adapter type.


## [1.2.0] - 2015-09-10
### Added
- Support for per request timeouts via {get,post,put,...}(..., timeout=10)


## [1.1.0] - 2015-09-09
### Changed
- xml serializer support
- multi header support of HeaderAuth
- `Service(trailing_slash=True)` will always append a slash

### Fixed
- urn-less support for APIs that don't have a fixed urn


## [1.0.0] - 2014-01-25
### Changed
- First stable release


[2.3]: https://github.com/mayfield/syndicate/compare/v2.1.2...v2.3
[2.1.2]: https://github.com/mayfield/syndicate/compare/v2.1.1...v2.1.2
[2.1.1]: https://github.com/mayfield/syndicate/compare/v2.1...v2.1.1
[2.1]: https://github.com/mayfield/syndicate/compare/v2...v2.1
[2]: https://github.com/mayfield/syndicate/compare/v1.4.0...v2
[1.4.0]: https://github.com/mayfield/syndicate/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/mayfield/syndicate/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/mayfield/syndicate/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/mayfield/syndicate/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/mayfield/syndicate/compare/b9ec552eb9967c5622053c33b0b0a4789a16ffab...v1.0.0
