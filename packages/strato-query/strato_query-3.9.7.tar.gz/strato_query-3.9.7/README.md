# Strato-Query
tools to help create queries to StratoDem's API

## Installation and usage
#### Python:
```
$ pip install strato-query
```

#### R:
```
library(devtools)
devtools::install_github('StratoDem/strato-query')
```

### Authentication
`strato_query` looks for an `API_TOKEN` environment variable.
```bash
# Example passing a StratoDem Analytics API token to a Python file using the API
$ API_TOKEN=my-api-token-here python examples/examples.py
```

### Median household income for 80+ households across the US, by year
#### Python:
```python
from strato_query.base_API_query import *
from strato_query.standard_filters import *


# Finds median household income in the US for those 80+ from 2010 to 2013
df = BaseAPIQuery.query_api_df(
    query_params=APIMedianQueryParams(
        query_type='MEDIAN',
        table='incomeforecast_us_annual_income_group_age',
        data_fields=('year', {'median_value': 'median_income'}),
        median_variable_name='income_g',
        data_filters=(
            GtrThanOrEqFilter(var='age_g', val=17).to_dict(),
            BetweenFilter(var='year', val=[2010, 2013]).to_dict(),
        ),
        groupby=('year',),
        order=('year',),
        aggregations=(),
    )
)

print('Median US household income 80+:')
print(df.head())
```
#### R:
```R
library(stRatoquery)


# Finds median household income in the US for those 80+ from 2010 to 2013
df = submit_api_query(
  query = median_query_params(
    table = 'incomeforecast_us_annual_income_group_age',
    data_fields = api_fields(fields_list = list('year', 'geoid2', list(median_value = 'median_hhi'))),
    data_filters = list(
        ge_filter(filter_variable = 'age_g', filter_value = 17),
        between_filter(filter_variable = 'year', filter_value = c(2010, 2013))
    ),
    groupby=c('year'),
    median_variable_name='income_g',
    aggregations=list()
  ),
  apiToken = 'my-api-token-here')

print('Median US household income 80+:')
print(head(df))
```

Output:
```
Median US household income 80+:
   MEDIAN_VALUE  YEAR
0         27645  2010
1         29269  2011
2         30474  2012
3         30712  2013
```

### Population density in the Boston MSA
#### Python:
```python
from strato_query.base_API_query import *
from strato_query.standard_filters import *


df = BaseAPIQuery.query_api_df(
    query_params=APIQueryParams(
        query_type='COUNT',
        table='populationforecast_metro_annual_population',
        data_fields=('year', 'cbsa', {'population': 'population'}),
        data_filters=(
            LessThanFilter(var='year', val=2015).to_dict(),
            EqFilter(var='cbsa', val=14454).to_dict(),
        ),
        aggregations=(dict(aggregation_func='sum', variable_name='population'),),
        groupby=('cbsa', 'year'),
        order=('year',),
        join=APIQueryParams(
            query_type='AREA',
            table='geocookbook_metro_na_shapes_full',
            data_fields=('cbsa', 'area', 'name'),
            data_filters=(),
            groupby=('cbsa', 'name'),
            aggregations=(),
            on=dict(left=('cbsa',), right=('cbsa',)),
        )
    )
)

df['POP_PER_SQ_MI'] = df['POPULATION'].div(df['AREA'])
df_final = df[['YEAR', 'NAME', 'POP_PER_SQ_MI']]

print('Population density in the Boston MSA up to 2015:')
print(df_final.head())
print('Results truncated')
```

#### R:
```R
library(stRatoquery)

df = submit_api_query(
  query = api_query_params(
    table = 'populationforecast_metro_annual_population',
    data_fields = api_fields(fields_list = list('year', 'cbsa', list(population = 'population'))),
    data_filters = list(
        lt_filter(filter_variable = 'year', filter_value = 2015),
        eq_filter(filter_variable = 'cbsa', filter_value = 14454)
    ),
    groupby=c('year'),
    aggregations = list(sum_aggregation(variable_name = 'population')),
    join = api_query_params(
        table = 'geocookbook_metro_na_shapes_full',
        query_type = 'AREA',
        data_fields = api_fields(fields_list = list('cbsa', 'area', 'name')),
        data_filters = list(),
        groupby = c('cbsa', 'name'),
        aggregations = list(),
        on = list(left = c('cbsa'), right = c('cbsa'))
    )
  ),
  apiToken = 'my-api-token-here')
```

Output:
```
Population density in the Boston MSA up to 2015:
   YEAR        NAME  POP_PER_SQ_MI
0  2000  Boston, MA    1139.046639
1  2001  Boston, MA    1149.129937
2  2002  Boston, MA    1153.094740
3  2003  Boston, MA    1152.352351
4  2004  Boston, MA    1149.932307
Results truncated
```

### Example use of query base class with API call and example filter
```python
from strato_query.base_API_query import *
from strato_query.standard_filters import *


class ExampleAPIQuery(BaseAPIQuery):
    @classmethod
    def get_df_from_API_call(cls, **kwargs):
        # This API call will return the population 65+ in 2018 within 5 miles of the lat/long pair
        age_filter = GtrThanOrEqFilter(
            var='age_g',
            val=14).to_dict()

        year_filter = EqFilter(
            var='year',
            val=2018).to_dict()

        mile_radius_filter = dict(
            filter_type='mile_radius',
            filter_value=dict(
                latitude=26.606484,
                longitude=-81.851531,
                miles=5),
            filter_variable='')

        df = cls.query_api_df(
            query_params=APIQueryParams(
                table='populationforecast_tract_annual_population_age',
                data_fields=('POPULATION',),
                data_filters=(age_filter, year_filter, mile_radius_filter),
                query_type='COUNT',
                aggregations=(),
                groupby=()
            )
        )

        return df
```
