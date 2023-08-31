# Change Log for RegEx4Seq Project

Following the style in https://keepachangelog.com/en/1.0.0/

## [0.3.0] Improved and unified the matches method, 2023-08-31

## Added

- The signature of `.matches`` has additional optional arguments. In particular
  the all_prefixes arguments gives a means for finding all possible matches of
  a match group.

- The signatures of `.findAllMatches` has been unified with `.matches`.

- Reduced the number of gaps in the documentation.

- CircleCI integration.
