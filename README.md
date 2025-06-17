# Municipal distances


## Setup

### Packages
This project uses pdm to manage packages. 

Try running `pdm install`. If that doesn't work you have to install pdm. 

Follow instructions [here](https://pdm-project.org/en/latest/#__tabbed_1_1)

### API keys

make a file called `.env` in the root and add your google maps api key like: 

```
GOOGLE_MAPS_API_KEY=your-key
```


## Code

All the magic happens in the distance_matrix_calculation.ipynb notebook with api calls happening in `src/google_maps_funcs.py`

## Data

The interesting datasets are in `data/result` and municipal info in `data/admsenternavn_coordinates.csv`