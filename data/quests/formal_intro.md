---
type: quest
id: formal_intro
name: Formal Introduction
description: Meet the leaders of the town.
---

# Started
```trigger
event: LOCATION_VISITED
location: market
```
```flow
pc: The Mayor told me to introduce myself to the Guard Captain.
pc: I should head to the Guardhouse.
```

# Goals

## Talk to the Mayor
```trigger
event: CHAR_MET
char: mayor
```
```flow
mayor: It is good to see you again. Have you met Captain Thorne yet?
```

## Visit the Guardhouse
```trigger
event: LOCATION_VISITED
location: guardhouse
```
```flow
pc: This must be the Guardhouse.
```

## Talk to the Guard Captain
```trigger
event: CHAR_MET
char: guard_captain
```
```flow
guard_captain: The Mayor mentioned you. We appreciate any law-abiding citizens here.
```

# Passed
```flow
$ achievements.unlock("social_butterfly")
pc: I've made some important connections today.
```
