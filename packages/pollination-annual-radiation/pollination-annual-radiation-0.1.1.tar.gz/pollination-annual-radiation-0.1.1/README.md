# Annual Radiation

Annual radiation recipe for Pollination

This recipe calculate the annual radiation for each timestep provided by the wea file.
The outputs are stored under `results/direct` and `results/total`. Nigh-time hours are
filtered before running the simulation. To match the results for each hours see the list
of hours in sun-up-hours.txt.

# Process

This recipe calculates the total amount of Radiation by calculating the direct sunlight
radiation from sun disks and adding them to the contribution from indirect sky radiation.

```
Total radiation = direct sun radiation + indirect sky radiation
```

The number of bounces for direct radiation is set to 0 and cannot be modified by user.
You can adjust the number of bounces for indirect sky radiation.

# Limitations

This recipe is limited to calculating up to `9999` number of suns at a time. This means
you might need to break down the annual studies with smaller timesteps into smaller
runs. This limitation is a result of how Radiance sets a limit on number of modifiers
in a single run. [See here](https://discourse.radiance-online.org/t/increase-maximum-number-of-modifiers-in-rcontrib/4684). We can address this limitation by either building our own version of Radiance
or breaking down the modifier list and looping over them and merging back the results.

