# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed

## [0.4.1] - 2021-02-25
### Added

- Initial architecture for rule plugins to allow custom rules. This
  initial release should be considered *beta* until the release of
  0.5.0.
- Add tests for dbt 0.19.0.
- General increased parsing coverage.
- Added some missing Postgres syntax elements.
- Added some basic introspection API elements to output what dialects
  and rules are available for use within the API.

### Changed

- Fix several Snowflake parsing bugs.
- Refactor from clause to handle flattens after joins.
- Fix .get_table_references() in Snowflake dialect.
- Macros defined within the .sqlfluff config will take precedence over the macros defined in the
  path that is defined with config value `sqlfluff:templater:jinja:load_macros_from_path`.
- Fix Snowflake indent parsing.
- Fixed incorrect parsing of syntax-like elements in comments.
- Altered parsing of `NULL` keywords, so parse as Literals where
  appropriate.
- Fixed bug in expression parsing leading to recursion errors.

## [0.4.0] - 2021-02-14
### Added

- Public API to enable people to import `sqlfluff` as a python module
  and call `parse`, `lint` and `fix` within their own projects. See
  [the docs](https://docs.sqlfluff.com/en/latest/api.html) for more
  information. ([#501](https://github.com/sqlfluff/sqlfluff/pull/501))
- The ability to use `dbt` as a templating engine directly allowing
  richer and more accurate linting around `dbt` macros (and packages
  related to `dbt`). For more info see [the docs](https://docs.sqlfluff.com/en/latest/configuration.html#dbt-project-configuration). ([#508](https://github.com/sqlfluff/sqlfluff/pull/508))
- Support for modulo (`%`) operator. ([#447](https://github.com/sqlfluff/sqlfluff/pull/447))
- A limit in the internal fix routines to catch any infinite loops. ([#494](https://github.com/sqlfluff/sqlfluff/pull/494))
- Added the `.istype()` method on segments to more intelligently
  deal with type matching in rules when inheritance is at play.
- Added the ability for the user to add their own rules when interacting
  with the `Linter` directly using `user_rules`.
- Added L034 'Fields should be stated before aggregates / window functions' per
  [dbt coding convenventions](https://github.com/fishtown-analytics/corp/blob/master/dbt_coding_conventions.md#sql-style-guide.) ([#495](https://github.com/sqlfluff/sqlfluff/pull/495))
- Templating tags, such as `{{ variables }}`, `{# comments #}` and
  `{% loops %}` (in jinja) now have placeholders in the parsed
  structure. Rule L003 (indentation), also now respects these
  placeholders so that their indentation is linted accordingly.
  For loop or block tags, they also generate an `Indent` and
  `Dedent` tag accordingly (which can be enabled or disabled)
  with a configuration value so that indentation around these
  functions can be linted accordingly. ([#541](https://github.com/sqlfluff/sqlfluff/pull/541))
- MyPy type linting into a large proportion of the core library. ([#526](https://github.com/sqlfluff/sqlfluff/pull/526), [#580](https://github.com/sqlfluff/sqlfluff/pull/580))
- Config values specific to a file can now be defined using a comment
  line starting with `-- sqlfluff:`. ([#541](https://github.com/sqlfluff/sqlfluff/pull/541))
- Added documentation for `--noqa:` use in rules. ([#552](https://github.com/sqlfluff/sqlfluff/pull/552))
- Added `pre-commit` hooks for `lint` and `fix`. ([#576](https://github.com/sqlfluff/sqlfluff/pull/576))
- Added a fix routine for Rule L019 (comma placement). ([#575](https://github.com/sqlfluff/sqlfluff/pull/575))
- Added Rule L031 to enforce "avoid using alias in the `FROM`/`JOIN` clauses" from the `dbt` coding conventions. ([#473](https://github.com/sqlfluff/sqlfluff/pull/473), [#479](https://github.com/sqlfluff/sqlfluff/pull/479))
- Added Rule L032 to enforce "do not use `USING`" from the `dbt` coding conventions. ([#487](https://github.com/sqlfluff/sqlfluff/pull/487))
- Added Rule L033 to enforce "prefer `UNION ALL` to `UNION *`" from the `dbt` coding conventions. ([#489](https://github.com/sqlfluff/sqlfluff/pull/489))
- Added Rule L034 to enforce "fields should be stated before aggregate/window functions" from the `dbt` coding conventions. ([#495](https://github.com/sqlfluff/sqlfluff/pull/495))
- Added Rule L038 to forbid (or require) trailing commas in select clauses. ([#362](https://github.com/sqlfluff/sqlfluff/pull/752))
- Added Rule L039 to lint unnecessary whitespace between elements. ([#502](https://github.com/sqlfluff/sqlfluff/pull/753))
- Added a fix routine for L015. ([#732](https://github.com/sqlfluff/sqlfluff/pull/732))
- Added a fix routine for L025. ([#404](https://github.com/sqlfluff/sqlfluff/pull/741))
- Adopted the `black` coding style. ([#485](https://github.com/sqlfluff/sqlfluff/pull/485))
- Added validation and documentation for rule configuration options. ([#462](https://github.com/sqlfluff/sqlfluff/pull/462))
- Added documentation for which rules are fixable. ([#594](https://github.com/sqlfluff/sqlfluff/pull/594))
- Added `EPOCH` keyword for postgres dialect. ([#522](https://github.com/sqlfluff/sqlfluff/pull/522))
- Added column index identifier in snowflake dialect. ([#458](https://github.com/sqlfluff/sqlfluff/pull/458))
- Added `USE` statement to the snowflake dialect. ([#537](https://github.com/sqlfluff/sqlfluff/pull/537))
- Added `CODE_OF_CONDUCT` to the project. ([#471](https://github.com/sqlfluff/sqlfluff/pull/471))
- Added `ISNULL` and `NOTNULL` keywords to ansi dialect. ([#441](https://github.com/sqlfluff/sqlfluff/pull/441))
- Added support for python 3.9. ([#482](https://github.com/sqlfluff/sqlfluff/pull/482))
- Added `requirements_dev.txt` for local testing/linting. ([#500](https://github.com/sqlfluff/sqlfluff/pull/500))
- Added CLI option `--disregard-sqlfluffignores` to allow direct linting of files in the `.sqlfluffignore`. ([#486](https://github.com/sqlfluff/sqlfluff/pull/486))
- Added `dbt` `incremental` macro. ([#363](https://github.com/sqlfluff/sqlfluff/pull/363))
- Added links to cockroachlabs expression grammars in ansi dialect. ([#592](https://github.com/sqlfluff/sqlfluff/pull/592))
- Added favicon to the docs website. ([#589](https://github.com/sqlfluff/sqlfluff/pull/589))
- Added `CREATE FUNCTION` syntax for postgres and for bigquery. ([#325](https://github.com/sqlfluff/sqlfluff/pull/325))
- Added `CREATE INDEX` and `DROP INDEX` for mysql. ([#740](https://github.com/sqlfluff/sqlfluff/pull/748))
- Added `IGNORE NULLS`, `RESPECT NULLS`, `GENERATE_DATE_ARRAY` and
  `GENERATE_TIMESTAMP_ARRAY` for bigquery. (
  [#667](https://github.com/sqlfluff/sqlfluff/pull/727),
  [#527](https://github.com/sqlfluff/sqlfluff/pull/726))
- Added `CREATE` and `CREATE ... CLONE` for snowflake. ([#539](https://github.com/sqlfluff/sqlfluff/pull/670))
- Added support for EXASOL. ([#684](https://github.com/sqlfluff/sqlfluff/pull/684))

### Changed

- Fixed parsing of semi-structured objects in the snowflake of dialects
  with whitespace gaps. [#634](https://github.com/sqlfluff/sqlfluff/issues/635)
- Handle internal errors elegantly, reporting the stacktrace and the
  error-surfacing file. [#632](https://github.com/sqlfluff/sqlfluff/pull/632)
- Improve message for when an automatic fix is not available for L004. [#633](https://github.com/sqlfluff/sqlfluff/issues/633)
- Linting errors raised on templated sections are now ignored by default
  and added a configuration value to show them. ([#713](https://github.com/sqlfluff/sqlfluff/pull/745))
- Big refactor of logging internally. `Linter` is now decoupled from
  logging so that it can be imported directly by subprojects without
  needing to worry about weird output or without the log handing getting
  in the way of your project. ([#460](https://github.com/sqlfluff/sqlfluff/pull/460))
- Linting errors in the final file are now reported with their position
  in the source file rather than in the templated file. This means
  when using sqlfluff as a plugabble library within an IDE, the
  references match the file which is being edited. ([#541](https://github.com/sqlfluff/sqlfluff/pull/541))
- Created new Github Organisation (https://github.com/sqlfluff) and
  migrated from https://github.com/alanmcruickshank/sqlfluff to
  https://github.com/sqlfluff/sqlfluff. ([#444](https://github.com/sqlfluff/sqlfluff/issues/444))
- Changed the handling of `*` and `a.b.*` expressions to have their
  own expressions. Any dependencies on this structure downstream
  will be broken. This also fixes the linting of both kinds of expressions
  with regard to L013 and L025. ([#454](https://github.com/sqlfluff/sqlfluff/pull/454))
- Refactor of L022 to handle poorly formatted CTEs better. ([#494](https://github.com/sqlfluff/sqlfluff/pull/494))
- Restriction of L017 to only fix when it would delete whitespace or
  newlines. ([#598](https://github.com/sqlfluff/sqlfluff/pull/756))
- Added a configuration value to L016 to optionally ignore lines
  containing only comments. ([#299](https://github.com/sqlfluff/sqlfluff/pull/751))
- Internally added an `EphemeralSegment` to aid with parsing efficiency
  without altering the end structure of the query. ([#491](https://github.com/sqlfluff/sqlfluff/pull/491))
- Split `ObjectReference` into `ColumnReference` and `TableReference`
  for more useful API access to the underlying structure. ([#504](https://github.com/sqlfluff/sqlfluff/pull/504))
- `KeywordSegment` and the new `SymbolSegment` both now inherit
  from `_ProtoKeywordSegment` which allows symbols to match in a very
  similar way to keywords without later appearing with the `type` of
  `keyword`. ([#504](https://github.com/sqlfluff/sqlfluff/pull/504))
- Introduced the `Parser` class to parse a lexed query rather than
  relying on users to instantiate a `FileSegment` directly. As a result
  the `FileSegment` has been moved from the core parser directly into
  the dialects. Users can refer to it via the `get_root_segment()`
  method of a dialect. ([#510](https://github.com/sqlfluff/sqlfluff/pull/510))
- Several perfomance improvements through removing unused functionality,
  sensible caching and optimising loops within functions. ([#526](https://github.com/sqlfluff/sqlfluff/pull/526))
- Split up rule tests into separate `yml` files. ([#553](https://github.com/sqlfluff/sqlfluff/pull/553))
- Allow escaped quotes in strings. ([#557](https://github.com/sqlfluff/sqlfluff/pull/557))
- Fixed `ESCAPE` parsing in `LIKE` clause. ([#566](https://github.com/sqlfluff/sqlfluff/pull/566))
- Fixed parsing of complex `BETWEEN` statements. ([#498](https://github.com/sqlfluff/sqlfluff/pull/498))
- Fixed BigQuery `EXCEPT` clause parsing. ([#472](https://github.com/sqlfluff/sqlfluff/pull/472))
- Fixed Rule L022 to respect leading comma configuration. ([#455](https://github.com/sqlfluff/sqlfluff/pull/455))
- Improved instructions on adding a virtual environment in the `README`. ([#457](https://github.com/sqlfluff/sqlfluff/pull/457))
- Improved documentation for passing CLI defaults in `.sqlfluff`. ([#452](https://github.com/sqlfluff/sqlfluff/pull/452))
- Fix bug with templated blocks + `capitalisation_policy = lower`. ([#477](https://github.com/sqlfluff/sqlfluff/pull/477))
- Fix array accessors in snowflake dialect. ([#442](https://github.com/sqlfluff/sqlfluff/pull/442))
- Color `logging` warnings red. ([#497](https://github.com/sqlfluff/sqlfluff/pull/497))
- Allow whitespace before a shorthand cast. ([#544](https://github.com/sqlfluff/sqlfluff/pull/544))
- Silenced warnings when fixing from stdin. ([#522](https://github.com/sqlfluff/sqlfluff/pull/522))
- Allow an underscore as the first char in a semi structured element key. ([#596](https://github.com/sqlfluff/sqlfluff/pull/596))
- Fix PostFunctionGrammar in the Snowflake dialect which was causing strange behaviour in L012. ([#619](https://github.com/sqlfluff/sqlfluff/pull/619/files))
- `Bracketed` segment now obtains its brackets directly from the dialect
  using a set named `bracket_pairs`. This now enables better configuration
  of brackets between dialects. ([#325](https://github.com/sqlfluff/sqlfluff/pull/325))

### Removed
- Dropped support for python 3.5. ([#482](https://github.com/sqlfluff/sqlfluff/pull/482))
- From the CLI, the `--no-safety` option has been removed, the default
  is now that all enabled rules will be fixed. ([#583](https://github.com/sqlfluff/sqlfluff/pull/583))
- Removed `BaseSegment.grammar`, `BaseSegment._match_grammar()` and
  `BaseSegment._parse_grammar()` instead preferring references directly
  to `BaseSegment.match_grammar` and `BaseSegment.parse_grammar`. ([#509](https://github.com/sqlfluff/sqlfluff/pull/509))
- Removed `EmptySegmentGrammar` and replaced with better non-code handling
  in the `FileSegment` itself. ([#509](https://github.com/sqlfluff/sqlfluff/pull/509))
- Remove the `ContainsOnly` grammar as it remained only as an anti-pattern. ([#509](https://github.com/sqlfluff/sqlfluff/pull/509))
- Removed the `expected_string()` functionality from grammars and segments ([#509](https://github.com/sqlfluff/sqlfluff/pull/509))
  as it was poorly supported.
- Removed `BaseSegment.as_optional()` as now this functionality happens
  mostly in grammars (including `Ref`). ([#509](https://github.com/sqlfluff/sqlfluff/pull/509))
- Removed `ColumnExpressionSegment` in favour of `ColumnReference`. ([#512](https://github.com/sqlfluff/sqlfluff/pull/512))
- Removed the `LambdaSegment` feature, instead replacing with an internal
  to the grammar module called `NonCodeMatcher`. ([#512](https://github.com/sqlfluff/sqlfluff/pull/512))
- Case sensitivity as a feature for segment matching has been removed as
  not required for existing dialects. ([#517](https://github.com/sqlfluff/sqlfluff/pull/517))
- Dependency on `difflib` or `cdifflib`, by relying on source mapping
  instead to apply fixes. ([#541](https://github.com/sqlfluff/sqlfluff/pull/541))

## [0.3.6] - 2020-09-24

### Added

- `sqlfluff dialects` command to get a readout of available
  dialects [+ associated docs].
- More helpful error messages when trying to run in Python2.
- Window functions now parse with `IGNORE`/`RESPECT` `NULLS`.
- Parsing of `current_timestamp` and similar functions. Thanks [@dmateusp](https://github.com/dmateusp).
- Snowflake `QUALIFY` clause.

### Changed

- Respect user config directories. Thanks [@sethwoodworth](https://github.com/sethwoodworth).
- Fix incorrect reporting of L013 with `*`. Thanks [@dmateusp](https://github.com/dmateusp).
- Fix incorrect reporting of L027 with column aliases. Thanks [@pwildenhain](https://github.com/pwildenhain).
- Simplification of application of fixes and correction of
  a case where fixes could be depleted. Thanks [@NiallRees](https://github.com/NiallRees).
- Fix functions with a similar structure to `SUBSTRING`.
- Refactor BigQuery `REPLACE` and `EXCEPT` clauses.
- Bigquery date parts corrected.
- Snowflake array accessors.
- Psotgres `NOTNULL` and `ISNULL`.
- Bugfix in snowflake for keywords used in semistructured
  queries.
- Nested `WITH` statements now parse.
- Performance improvements in the `fix` command.
- Numeric literals starting with a decimal now parse.
- Refactor the jinja templater.

## [0.3.5] - 2020-08-03

### Added

- Patterns and Anti-patterns in documentation. Thanks [@flpezet](https://github.com/flpezet).
- Functions in `GROUP BY`. Thanks [@flpezet](https://github.com/flpezet).

### Changed

- Deep bugfixes in the parser to handle simple matching better for a few
  edge cases. Also added some logging deeper in the parser.
- Added in the `SelectableGrammar` and some related segments to make it
  easier to refer to _select-like_ things in other grammars.
- Fixes to `CASE` statement parsing. Thanks [@azhard](https://github.com/azhard).
- Fix to snowflake `SAMPLE` implementation. Thanks [@rkm3](https://github.com/rkm3).
- Numerous docs fixes. Thanks [@SimonStJG](https://github.com/SimonStJG),
  [@flpezet](https://github.com/flpezet), [@s-pace](https://github.com/s-pace),
  [@nolanbconaway](https://github.com/nolanbconaway).

## [0.3.4] - 2020-05-13

### Changed

- Implementation of the bigquery `CREATE MODEL` syntax. Thanks [@barrywhart](https://github.com/barrywhart).
- Bugfixes for:
  - Edge cases for L006
  - False alarms on L025
  - `ORDER BY x NULLS FIRST|LAST`
  - `FOR` keyword in bigquery `SYSTEM_TIME` syntax.

## [0.3.3] - 2020-05-11

### Added

- Added the `--nofail` option to `parse` and `lint` commands to assist
  rollout.
- Added the `--version` option to complement the `version` option already
  available on the cli.
- Parsing for `ALTER TABLE`.
- Warning for unset dialects when getting parsing errors.
- Configurable line lengths for output.

## [0.3.2] - 2020-05-08

### Added

- Support for the Teradata dialect. Thanks [@Katzmann1983](https://github.com/Katzmann1983)!
- A much more detailed getting started guide in the docs.
- For the `parse` command, added the `--profiler` and `--bench` options
  to help debugging performance issues.
- Support for the `do` command in the jinja templater.
- Proper parsing of the concatenate operator (`||`).
- Proper indent handling of closing brackets.
- Logging and benchmarking of parse performance as part of the CI pipeline.
- Parsing of object references with defaults like `my_db..my_table`.
- Support for the `INTERVAL '4 days'` style interval expression.
- Configurable trailing or leading comma linting.
- Configurable indentation for `JOIN` clauses.
- Rules now have their own logging interface to improve debugging ability.
- Snowflake and Postgres dialects.
- Support for a `.sqlfluffignore` file to ignore certain paths.
- More generic interfaces for managing keywords in dialects, including `set`
  interfaces for managing and creating keywords and the `Ref.keyword()` method
  to refer to them, and the ability to refer directly to keyword names in
  most grammars using strings directly. Includes `SegmentGenerator` objects
  to bind dialect objects at runtime from sets. Thanks [@Katzmann1983](https://github.com/Katzmann1983)!
- Rule `L029` for using unreserved keywords as variable names.
- The jinja templater now allows macros loaded from files, and the
  hydration of variables ending in `_path` in the config files.
- JSON operators and the `DISTINCT ON ()` syntax for the postgres dialect.

### Changed

- Refactor of whitespace and non-code handling so that segments are
  less greedy and default to not holding whitespace on ends. This allows
  more consistent linting rule application.
- Change config file reading to *case-sensitive* to support case
  sensitivity in jinja templating.
- Non-string values (including lists) now function in the python
  and jinja templating libraries.
- Validation of the match results of grammars has been reduced. In
  production cases the validation will still be done, but only on
  *parse* and not on *match*.
- At low verbosities, python level logging is also reduced.
- Some matcher rules in the parser can now be classified as _simple_
  which allows them to shortcut some of the matching routines.
- Yaml output now double quotes values with newlines or tab characters.
- Better handling on hanging and closing indents when linting rule L003.
- More capable handline of multi-line comments so that indentation
  and line length parsing works. This involves some deep changes to the
  lexer.
- Getting violations from the linter now automatically takes into account
  of ignore rules and filters.
- Several bugfixes, including catching potential infinite regress during
  fixing of files, if one fix would re-introduce a problem with another.
- Behaviour of the `Bracketed` grammar has been changed to treat its
  content as a `Sequence` rather than a `OneOf`.
- Move to `SandboxedEnvironment` rather than `Environment` for jinja
  templating for security.
- Improve reporting of templating issues, especially for the jinja templater
  so that missing variables are rendered as blanks, but still reported as
  templating violations.

## [0.3.1] - 2020-02-17

### Added

- Support for `a.b.*` on top of `a.*` in select target expressions.

## [0.3.0] - 2020-02-15

### Changed

- Deprecated python 2.7 and python 3.4 which are now both past
  their maintenance horizon. The 0.2.x branch will remain available
  for continued development for these versions.
- Rule L003 is now significantly smarter in linting indentation
  with support for hanging indents and comparison to the most
  recent line which doesn't have an error. The old (more simple)
  functionality of directly checking whether an indent was a
  multiple of a preset value has been removed.
- Fixed the "inconsistent" bug in L010. Thanks [@nolanbconaway](https://github.com/nolanbconaway).
- Updated logging of parsing and lexing errors to have more useful
  error codes.
- Changed parsing of expressions to favour functions over identifiers
  to [fix the expression bug](https://github.com/sqlfluff/sqlfluff/issues/96).
- Fixed the "inconsistent" bug in L010. Thanks [@nolanbconaway](https://github.com/nolanbconaway).
- Moved where the `SELECT` keyword is parsed within a select statement,
  so that it belongs as part of the newly renamed `select_clause` (renamed
  from previously `select_target_group`).
- Clarified handling of the `type` and `name` properties of the BaseSegment
  class and its children. `name` should be specific to a particular kind
  of segment, and `type` should express a wider group. Handling of the
  `newline`, `whitespace` and `comma` segments has been updated so that
  we use the `type` property for most use cases rather than `name`.

### Added

- *Meta segments* for indicating where things can be present in the parsed
  tree. This is mostly illustrated using the `Indent` and `Dedent` segments
  used for indicating the position of theoretical indents in the structure.
  Several helper functions have been added across the codebase to handle
  this increase in the kinds of segments which might be encountered by
  various grammars.
- Rule L016 has been added to lint long lines. In the `fix` phase of this
  rule, there is enough logic to try and reconstruct a sensible place for
  line breaks as re-flow the query. This will likely need further work
  and may still encounter places where it doesn't fix all errors but should
  be able to deal with the majority of simple cases.
- BigQuery dialect, initially just for appropriate quoting.
- Added parsing of DDL statements such as `COMMIT`, `DROP`, `GRANT`, `REVOKE`
  and `ROLLBACK`. Thanks [@barrywhart](https://github.com/barrywhart).
- `--format` option to the `parse` command that allows a yaml output. This
  is mostly to make test writing easier in the development process but
  might also be useful for other things.
- Parsing of set operations like `UNION`.
- Support for the `diff-cover` tool. Thanks [@barrywhart](https://github.com/barrywhart).
- Enabled the `fix` command while using `stdin`. Thanks [@nolanbconaway](https://github.com/nolanbconaway).
- Rule to detect incorrect use of `DISTINCT`. Thanks [@barrywhart](https://github.com/barrywhart).
- Security fixes from DeepCover. Thanks [@sanketsaurav](https://github.com/sanketsaurav).
- Automatic fix testing, to help support the newer more complicated rules.
- Interval literals
- Support for the `source` macro from dbt. Thanks [@Dandandan](https://github.com/Dandandan)
- Support for functions with spaces between the function name and the brackets
  and a linting rule `L017` to catch this.
- Efficiency cache for faster pruning of the parse tree.
- Parsing of array notation as using in BigQuery and Postgres.
- Enable the `ignore` parameter on linting and fixing commands to ignore
  particular kinds of violations.

## [0.2.4] - 2019-12-06

### Added

- A `--code-only` option to the `parse` command to spit out a more
  simplified output with only the code elements.
- Rules can now optionally override the description of the violation
  and pass that back via the `LintingResult`.

### Changed

- Bugfix, correct missing files in `setup.py` `install_requires` section.
- Better parsing of the *not equal* operator.
- Added more exclusions to identifier reserved words to fix cross joins.
- At verbosity levels 2 or above, the root config is printed and then any
  diffs to that for specific files are also printed.
- Linting and parsing of directories now reports files in alphabetical
  order. Thanks [@barrywhart](https://github.com/barrywhart).
- Better python 2.7 stability. Thanks [@barrywhart](https://github.com/barrywhart).
- Fixing parsing of `IN`/`NOT IN` and `IS`/`IS NOT`.

## [0.2.3] - 2019-12-02

### Changed

- Bugfix, default config not included.

## [0.2.2] - 2019-12-02

### Changed

- Tweek rule L005 to report more sensibly with newlines.
- Rework testing of rules to be more modular.
- Fix a config file bug if no root config file was present for some
  values. Thanks [@barrywhart](https://github.com/barrywhart).
- Lexing rules are now part of the dialect rather than a
  global so that they can be overriden by other dialects
  when we get to that stage.

## [0.2.0] - 2019-12-01

### Added

- Templating support (jinja2, python or raw).
  - Variables + Macros.
  - The `fix` command is also sensitive to fixing over templates
    and will skip certain fixes if it feels that it's conflicted.
- Config file support, including specifying context for the templater.
- Documentation via Sphinx and readthedocs.
  - Including a guide on the role of SQL in the real world.
    Assisted by [@barrywhart](https://github.com/barrywhart).
- Documentation LINTING (given we're a linting project) introduced in CI.
- Reimplemented L006 & L007 which lint whitespace around operators.
- Ability to configure rule behaviour direclty from the config file.
- Implemented L010 to lint capitalisation of keywords.
- Allow casting in the parser using the `::` operator.
- Implemented `GROUP BY`and `LIMIT`.
- Added `ORDER BY` using indexes and expressions.
- Added parsing of `CASE` statements.
- Support for window/aggregate functions.
- Added linting and parsing of alias expressions.

### Changed

- Fixed a bug which could cause potential infinite recursion in configuration
- Changed how negative literals are handled, so that they're now a compound segment
  rather than being identified at the lexing stage. This is to allow the parser
  to resolve the potential ambiguity.
- Restructure of rule definitions to be more streamlined and also enable
  autodocumentation. This includes a more complete `RuleSet` class which now
  holds the filtering code.
- Corrected logging in fix mode not to duplicate the reporting of errors.
- Now allows insert statements with a nested `with` clause.
- Fixed verbose logging during parsing.
- Allow the `Bracketed` grammar to optionally match empty brackets using
  the optional keyword.

## [0.1.5] - 2019-11-11

### Added

- Python 3.8 Support!

### Changed

- Moved some of the responsibility for formatted logging into the linter to mean that we can
  log progressively in large directories.
- Fixed a bug in the grammar where one of the return values was messed up.

## [0.1.4] - 2019-11-10

### Added

- Added a `--exclude-rules` argument to most of the commands to allow rule users
  to exclude specific subset of rules, by [@sumitkumar1209](https://github.com/sumitkumar1209)
- Added lexing for `!=`, `~` and `::`.
- Added a new common segment: `LambdaSegment` which allows matching based on arbitrary
  functions which can be applied to segments.
- Recursive Expressions for both arithmetic and functions, based heavily off the grammar
  provided by the guys at [CockroachDB](https://www.cockroachlabs.com/docs/stable/sql-grammar.html#select_stmt).
- An `Anything` grammar, useful in matching rather than in parsing to match anything.

### Changed

- Complete rewrite of the bracket counting functions, using some centralised class methods
  on the `BaseGrammar` class to support common matching features across multiple grammars.
  In particular this affects the `Delimited` grammar which is now *much simpler* but does
  also require *slightly* more liberal use of terminators to match effectively.
- Rather than passing around multiple variables during parsing and matching, there is now
  a `ParseContext` object which contains things like the dialect and various depths. This
  simplifies the parsing and matching code significantly.
- Bracket referencing is now done from the dialect directly, rather than in individual
  Grammars (except the `Bracketed` grammar, which still implements it directly). This
  takes out some originally duplicated code.
- Corrected the parsing of ordering keywords in and `ORDER BY` clause.

### Removed

- Removed the `bracket_sensitive_forward_match` method from the `BaseGrammar`. It was ugly
  and not flexible enough. It's been replaced by a suite of methods as described above.

## [0.1.3] - 2019-10-30

### Changed

- Tweak to the L001 rule so that it doesn't crash the whole thing.

## [0.1.2] - 2019-10-30

### Changed

- Fixed the errors raised by the lexer.

## [0.1.1] - 2019-10-30

### Changed

- Fixed which modules from sqlfluff are installed in the setup.py. This affects
  the `version` command.

## [0.1.0] - 2019-10-29

### Changed

- *Big Rewrite - some loss in functionality might be apparent compared
  to pre-0.1.0. Please submit any major problems as issues on github*
- Changed unicode handling for better escape codes in python 2.
  Thanks [@mrshu](https://github.com/mrshu)
- BIG rewrite of the parser, completely new architecture. This introduces
  breaking changes and some loss of functionality while we catch up.
  - In particular, matches now return partial matches to speed up parsing.
  - The `Delimited` matcher has had a significant re-write with a major
    speedup and broken the dependency on `Sequence`.
  - Rewrite of `StartsWith` and `Sequence` to use partial matches properly.
  - Different treatment of numeric literals.
  - Both `Bracketed` and `Delimited` respect bracket counting.
  - MASSIVE rewrite of `Bracketed`.
- Grammars now have timers.
- Joins properly parsing,
- Rewrite of logging to selectively output commands at different levels
  of verbosity. This uses the `verbosity_logger` method.
- Added a command line `sqlfluff parse` option which runs just the parsing step
  of the process to better understand how a file is being parsed. This also
  has options to configure how deep we recurse.
- Complete Re-write of the rules section, implementing new `crawlers` which
  implement the linting rules. Now with inbuilt fixers in them.
- Old rules removed and re implemented so we now have parity with the old rule sets.
- Moved to using Ref mostly within the core grammar so that we can have recursion.
- Used recursion to do a first implementation of arithmetic parsing. Including a test for it.
- Moved the main grammar into a seperate dialect and renamed source and test files accordingly.
- Moved to file-based tests for the ansi dialect to make it easier to test using the tool directly.
- As part of file tests - expected outcomes are now encoded in yaml to make it easier to write new tests.
- Vastly improved readability and debugging potential of the _match logging.
- Added support for windows line endings in the lexer.

## [0.0.7] - 2018-11-19

### Added

- Added a `sqlfluff fix` as a command to implement auto-fixing of linting
  errors. For now only `L001` is implemented as a rule that can fix things.
- Added a `rules` command to introspect the available rules.
- Updated the cli table function to use the `testwrap` library and also
  deal a lot better with longer values.
- Added a `--rules` argument to most of the commands to allow rule users
  to focus their search on a specific subset of rules.

### Changed

- Refactor the cli tests to use the click CliRunner. Much faster

## [0.0.6] - 2018-11-15

### Added

- Number matching

### Changed

- Fixed operator parsing and linting (including allowing the exception of `(*)`)

## [0.0.5] - 2018-11-15

### Added

- Much better documentation including the DOCS.md

### Changed

- Fixed comma parsing and linting

## [0.0.4] - 2018-11-14

### Added

- Added operator regexes
- Added a priority for matchers to resolve some ambiguity
- Added tests for operator regexes
- Added ability to initialise the memory in rules

## [0.0.3] - 2018-11-14

### Added

- Refactor of rules to allow rules with memory
- Adding comma linting rules (correcting the single character matchers)
- Adding mixed indentation linting rules
- Integration with CircleCI, CodeCov and lots of badges

### Changed

- Changed import of version information to fix bug with importing config.ini
- Added basic violations/file reporting for some verbosities
- Refactor of rules to simplify definition
- Refactor of color cli output to make it more reusable

## [0.0.2] - 2018-11-09

### Added

- Longer project description
- Proper exit codes
- colorama for colored output

### Changed

- Significant CLI changes
- Much improved output from CLI

## [0.0.1] - 2018-11-07

### Added

- Initial Commit! - VERY ALPHA
- Restructure into [package layout](https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure)
- Adding Tox and Pytest so that they work
