# Auto Index and Search Django Model Instances with RediSearch (using `redis-search-django`)

# Description

I **build** **[`redis-search-django`](https://github.com/saadmk11/redis-search-django)** (**Django Package**) as a part of **Redis Hackathon on DEV**. 
**`redis-search-django`** is a package that provides **auto indexing** and **searching** capabilities for Django model instances using **[RediSearch](https://redis.io/docs/stack/search/)**. 
This is a Demo App that uses `redis-search-django` package to Showcase a Product Search Engine with **auto indexing** and **searching**.


### App Screenshot

![RediSearch Django](https://user-images.githubusercontent.com/24854406/185760945-18bacae6-af2e-48bd-a412-d6fac878fd0c.png)

## How it works

### How the data is stored:

1. The App uses **RedisJSON** to **store the data** in Redis.

Example Unit of data:

```json
{
    "pk": "306",
    "vendor": {
        "pk": "306",
        "identifier": "3de47386-ffe9-4512-8161-6f96f853cf9a",
        "name": "Company-2",
        "email": "company-2@example.com",
        "establishment_date": "2022-08-20",
    },
    "category": {
        "pk": "7",
        "custom_field": "CUSTOM FIELD VALUE",
        "name": "Shoes",
        "slug": "shoes",
    },
    "tags": [{"pk": "7", "name": "Brand 1"}, {"pk": "12", "name": "Model 3"}],
    "name": "TIVO HD DIGITAL VIDEO RECORDER (180 HOUR) - TCD652160",
    "description": "TiVo HD Digital Video Recorder - TCD652160/ Search, Record And Watch Shows In HD/ Record Up To 20 Hours In HD (Or 180 Hours In Standard Definition)/ Record Two Shows At Once In HD/ Replaces Your Cable Box And Works With Over-The-Air Antenna/ USB Connectivity/ Remote Control/ Netflix Instant Streaming/ TiVo Service Required And Sold Separately",
    "price": 10,
    "created_at": "2022-08-20T14:09:24.253934+00:00",
    "quantity": 1,
    "available": 1
}
```

2. The App also creates index schema (using `redis-search-django` and `redis-om`) for each Django Model so that we can perform search operation on it using **RediSearch**.

Example Index Schema Generation Command created by `redis-search-django` and `redis-om`:

```bash
ft.create CategoryDocument:index ON JSON PREFIX 1 CategoryDocument: SCHEMA $.pk AS pk TAG SEPARATOR | $.name AS name TAG SEPARATOR
```

### How the data is accessed:

1. The App uses **RedisJSON** to fetch specific Document.

Example:

```python
ProductDocument.get(pk=626)

# Generated Command:
# JSON.GET ProductDocument:626
```

2. The App uses **RediSearch** to perform search operation and filtering on the data.

Example:

```python
query_expression = (
    (
        ProductDocument.name % "Term"
        | ProductDocument.description % "Term"
    )
    & (ProductDocument.price >= float(10) & ProductDocument.price <= float(100))
    & (ProductDocument.tags.name << ["Black", "Blue"])
)

ProductDocument.find(query_expression).sort_by("-price").execute()

# Generated Command:
# FT.SEARCH redis_search:products.documents.ProductDocument:index (((((@name_fts:Term)| (@description_fts:Term)) (@price:[1.0 +inf])) (@price:[-inf 10.0])) ((@tags_name:{Black|Blue})) LIMIT 0 30 SORTBY price desc
```

3. The App uses **RediSearch** to perform search aggregation on the data.

Example:

```python
ProductDocument.aggregate(
   ProductDocument.build_aggregate_request(ProductDocument.name % "Term").group_by(
       ["@tags_name"],
       reducers.count().alias("count"),
   )
)

# Generated Command:
# FT.AGGREGATE ProductDocument:index (((((@name_fts:Term))) GROUPBY 1 @tags_name REDUCE COUNT 0 AS count
```

## How to run it locally?

### Prerequisites

- Docker
- Docker Compose


### Local installation

#### Install Docker and Docker Compose for your OS

- Docker Setup Instructions: https://docs.docker.com/get-docker/
- Docker Compose Setup Instructions: https://docs.docker.com/compose/install/


#### Clone the repository:

```bash
git clone git@github.com:saadmk11/try-redis-search-django.git
```

#### Switch to the repository directory:

```bash
cd try-redis-search-django
```

#### Run Server:

The App include a **docker-compose.yaml** file that runs The Django server and Redis Stack. 

**Run:** 

```bash
docker-compose up  # Or, docker compose up
```

- Redis Stack Server will be available here: `redis://localhost:6379`
- Django Development Server will be available here: `http://localhost:8000`

- Search Page: `http://localhost:8000`
- Django Admin Page: `http://localhost:8000/admin` (Username: `admin`, Password: `12345`)


## External Resources

**Dataset:** https://github.com/etano/productner/blob/master/Product%20Dataset.csv

**Bootstrap Template:** https://www.bootdey.com/snippets/view/Filter-search-result-page

## Deployment

To make deploys work, you need to create free account on [Redis Cloud](https://redis.info/try-free-dev-to)

### Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy?template=https://github.com/saadmk11/try-redis-search-django)

## License

The code in this project is released under the [MIT License](LICENSE).
