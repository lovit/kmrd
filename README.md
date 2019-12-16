# Korean Movie Recommender system Dataset

MovieLens style dataset built from Naver Movie rating systems with [Naver Movie Scraper][scraper]

[scraper]: https://github.com/lovit/naver_movie_scraper

## Files of dataste

Dataset consists of following files.

### Movie Information File, `movies.txt`

Tap separated metadata table, (movie idx, Korean title, English title, first open year, grade)

```
movie	title	title_eng	year	grade
10107	아웃 오브 아프리카	Out Of Africa , 1985	1986	PG
13252	시계태엽 오렌지	A Clockwork Orange , 1971		청소년 관람불가
24452	매트릭스	The Matrix , 1999	2016	12세 관람가
39516	달콤한 인생	A Bittersweet Life , 2005	2005	청소년 관람불가
...
```

### People Information File, `peoples.txt`

Tap separated people name table, (people id, Korean name, English name)

```
people	korean	original
73	릴리 워쇼스키	Lilly Wachowski
214	캐리 앤 모스	Carrie-Anne Moss
554	헬레나 본햄 카터	Helena Bonham Carter
581	류승완	RYOO Seung-wan
688	제프 다니엘스	Jeff Daniels
1824	송강호	Song Kang-ho
1897	이범수	
1898	이병헌	Byung-hun Lee
1969	전도연	
2009	천호진	
...
```


### Casting Information File, `castings.csv`

Comma separated table, (movie id, people id, credit order, leading role)

- `reading` 1 means the people acts as leading role
```
movie,people,order,leading 
10107,1336,1,1
10107,1061,2,1
10107,892,3,0
10107,4879,4,0
10107,11143,5,0
10107,7020,6,0
...
```

### Rating matrix , `ratings.csv`

Comma separated table, (user index, movie id, rate, time)

- `rate` is 1 - 10 integer score
- `time` is UNIX time format

```
user,movie,rate,time
0,10107,10,1452358200
1,10107,5,1406125440
2,10107,8,1255014420
3,10107,7,1169798460
```


## KMRD-small


