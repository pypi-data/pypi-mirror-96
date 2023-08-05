# AWS Profile Utility

The `awsprofile` utility can be used to simplify working with a large number of profiles. This utility reads from `~/.aws/credentials` and `~/.aws/awsprofile` to list profiles.

## Install

```bash
pip install xawsprofile
```

## Usage

```bash
# list profiles
awsprofile list

# set profile to profile1 and set alias
eval $(awsprofile set profile1 --alias p1)

# list regions
awsprofile list-regions
```

## Bash Completion

This utility includes the following bash completions:

### Select Profile

`ap` (aws profile) - `ap {TAB}{TAB}` then select a profile, hit `{ENTER}`

```bash
$ ap prof{TAB}{TAB}
profile1     profile2
```

### Select Region

`ar` (aws region) - `ar {TAB}{TAB}`, then select a region, hit `{ENTER}`

```bash
$ ar us-{TAB}{TAB}
us-east-1     us-west-1
```

### Setup Bash Completion

```bash
# add to your .bash_profile
eval "$(awsprofile completion bash)"
```

## Commands

### List Profiles

`list` - list profiles

```bash
$ awsprofile list
profile1
profile2
```

### Set Profile

`set` - set the current profile using exported environment variables

```bash
$ eval(awsprofile set profile1)

# set profile and set alias
$ eval(awsprofile set profile1 --alias p1)
```

### List Regions

`list-regions` - list AWS regions

### Configure

`config` - configure awsprofiles

This currently supports `cwd` to configure the current working directory with a filter.

```bash
# filter only profiles-* and remove `profiles-` prefix
awsprofile config cwd --match 'profiles-(.*)`
```

## Customizations

### Aliases

To set an alias, update `~/.aws/awsprofile` or use `awsprofile set ... --alias ...` or use `ap {profile} {alias}`.

```bash
eval $(awsprofile set profile1 --alias p1)

ap profile1 p1
```

### Naming Rules

To simplify the profile names, rules can be applied when `awsprofile list` is run.

* global: ~/.aws/awsprofile
* working directory: {workdir}/.awsprofile (this overrides anything in global)

```text
# rename blah-* by removing "blah-" (ex: blah-test would be just test)
[naming cleanup-blah]
match = blah-(.*)
replace = \1

# hide test-*
[naming hide-test]
match = test-(.*)
visible = false

# hide all but test-*
[naming hide-others]
match = test-(.*)
negate = true
visible = false

# only applies to {workdir}/.awsprofile
[naming]
inherit_global = true
```

### Tips

* `awsprofile config cwd --match 'profiles-(.*)` will setup the current working directory to filter only `profiles-*` as well as strip `profiles-` from the profile names. This generates a `.awsprofile` in the current working directory.