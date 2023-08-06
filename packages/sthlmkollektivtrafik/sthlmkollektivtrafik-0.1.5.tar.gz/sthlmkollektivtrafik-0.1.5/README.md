# sthlmkollektivtrafik

## Download

> pip install sthlmkollektivtrafik

## Environment variable names
Store your api's as an environment variables with the names:

Plattsuppslag: SKT_location_api

Realtidsinformation: SKT_realtime_api

Storningsinformation: SKT_delay_api

Reseplanerare: SKT_planner_api

## Platsuppslag

### Examples

```python
from sthlmkollektivtrafik import platsuppslag

result = platsuppslag.search("searchString")

print("Name: {} Id: {}".format(result.name, result.id))
```

### Parameters

| Name          | Type          | Description              |
| ------------- | ------------- | ------------------------ |
| .name         | String        | name of the place        |
| .id           | Integer       | station id               |
| .type         | String        | station, adrees or POI   |
| .all          | json file     | everything               |
| .code         | Integer       | statuscode from call     |
| .responses    | Integer       | number of results        |
| .stations     | String-list   | all search-results, names|
| .log          | String-list   | log                      |

## Realtidsinformation

### Example

```python
from sthlmkollektivtrafik import realtidsinformation

result = realtidsinformation.departure("stationId", "timewindow")

for i in range(len(result.busDest)):
    print("{} {} - {}".format(result.busDest[i], result.busNum[i], result busTime[i]))
```

### Parameters

| Name                 | Type          | Description              |
| -------------------- | ------------- | ------------------------ |
| .all                 | json file     | everything               |
| .buses               | json file     | all bus departures       |
| .metros              | json file     | all metro departures     |
| .trains              | json file     | all train departures     |
|.(bus/metro/train)Dest| String-list   | ex .busDest              |
|.(bus/metro/train)Time| String-list   | ex .metroTime            |
|.(bus/metro/train)Num | String-list   | ex .trainNum             |
| .log                 | String-list   | log                      |

## Storningsinformation

### Example

```python
from sthlmkollektivtrafik import storningsinformation

result = realtidsinformation.departure("stationId")

print(result.headers[0])
print(result.details[0])

```

### Parameters

| Name                 | Type          | Description              |
| -------------------- | ------------- | ------------------------ |
| .all                 | json file     | everything               |
| .headers             | String-list   | titles                   |
| .details             | String-list   | text                     |
| .log                 | String-list   |log                       |

## Reseplanerare

### Example

```python
from sthlmkollektivtrafik import reseplanerare

result = reseplanerare.searchJourney("startId", "destId")

for leg in res.journey[0]:
    print("{} {}: Take {} to {} ".format(leg[1], leg[0], leg[2], leg[4]))

```

### Parameters

journey = [journey1, journey2, journey3...]

journey1 = [leg1, leg2, leg3....]

leg = [startTime, startName, transportName, destTime, destName]
