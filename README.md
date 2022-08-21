# Auto Index and Search Django Model Instances with RediSearch (using `redis-search-django`)

# Description

I built an **Installable Django Package** called **[`redis-search-django`](https://github.com/saadmk11/redis-search-django)** as a part of **[Redis Hackathon on DEV](https://dev.to/devteam/announcing-the-redis-hackathon-on-dev-3248)**. 
**`redis-search-django`** is a package that provides **auto indexing** and **searching** capabilities for Django model instances using **[RediSearch](https://redis.io/docs/stack/search/)**. 

This is a Demo App that uses `redis-search-django` package to Showcase a Product Search Engine with **auto indexing** and **searching**.

**redis-search-django Documentation:** https://github.com/saadmk11/redis-search-django


### App Screenshot

![RediSearch Django](https://user-images.githubusercontent.com/24854406/185760945-18bacae6-af2e-48bd-a412-d6fac878fd0c.png)

## How it works

### Create Search Document from Django Model. (Using `redis-search-django`)

**1. For Django Model:**

```python
# models.py

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30)

    def __str__(self) -> str:
        return self.name
```

**2. You can create a document class like this:**

**Note:** Document classes must be stored in `documents.py` file.

```python
# documents.py

from redis_search_django.documents import JsonDocument

from .models import Category


class CategoryDocument(JsonDocument):
    class Django:
        model = Category
        fields = ["name", "slug"]
```

**3. Run Index Django Management Command to create the index on Redis (Only need to run once to generate Index Schema on Redis):**

```bash
python manage.py index
```

**Note:** This will also populate the index with existing data from the database

Now **category objects** will be indexed **automatically** on **Redis** on **create/update/delete** events.

**More Complex Examples Can be found here:** https://github.com/saadmk11/redis-search-django

### How the data is stored:

1. The App uses **RedisJSON** to **store the data** into Redis.

```python
# Create Django Model Objects

vendor = Vendor.objects.create(name="New Vendor", establishment_date="2022-08-21")
category = Category.objects.create(name="Foods", slug="foods")
product = Product.objects.create(
    name="NEW PRODUCT", description="Product Description",
    price=20, vendor=vendor, category=category
)

tag = Tag.objects.create(name="Brand 1")
tag2 = Tag.objects.create(name="Brand 2")
product.tags.set([tag, tag2])


# After the Model Object Creation `redis-search-django` will automatically run this Command to update the Product Index

ProductDocument.from_model_instance(product_obj,save=True)

# Generated Command:
# JSON.SET ProductDocument:628 . {"pk": "628", "vendor": {"pk": "629", "identifier": "a9f75bd4-203f-42f0-aae6-93ba3366f7cd", "name": "New Vendor", "email": "test@test.com", "establishment_date": "2022-08-21"}, "category": {"pk": "1", "custom_field": "CUSTOM FIELD VALUE", "name": "Foods", "slug": "foods"}, "tags": [{"pk": "7", "name": "Brand 1"}, {"pk": "8", "name": "Brand 2"}], "name": "NEW PRODUCT", "description": "Product Description", "price": 20, "created_at": "2022-08-21T08:14:46.309872+00:00", "quantity": 1, "available": 1}
```

**Example Unit of data stored in Redis:**

```json
{
    "pk": "628",
    "vendor": { 
        "pk": "629",
        "identifier": "a9f75bd4-203f-42f0-aae6-93ba3366f7cd",
        "name": "New Vendor",
        "email": "test@test.com",
        "establishment_date": "2022-08-21"
    },
    "category": { "pk": "1", "custom_field": "CUSTOM FIELD VALUE", "name": "Foods", "slug": "foods" },
    "tags": [
        { "pk": "7", "name": "Brand 1" },
        { "pk": "8", "name": "Brand 2" }
    ],
    "name": "NEW PRODUCT",
    "description": "Product Description",
    "price": 20,
    "created_at": "2022-08-21T08:14:46.309872+00:00",
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
