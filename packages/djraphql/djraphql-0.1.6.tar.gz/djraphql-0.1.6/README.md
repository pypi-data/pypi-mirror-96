# DjraphQL

Check out the [documentation](https://radico.github.io/djraphql)!

## What

DjraphQL ("GiraffeQL") is a library that examines your Django models and builds a flexible, performant GraphQL schema using [Graphene](https://docs.graphene-python.org/en/latest/). No resolvers necessary.

You can of course extend this schema, reference the defined types and build custom business logic into your own resolvers. The goal is to remove the monotonous 90% of boilerplate generalized C.R.U.D. and allow you to focus on stuff that can't be auto-generated.

## How

You provide a list of Django models and some associated metadata. For example, you can define the QuerySet that will be used for each fetch of a certain model type (you have access to the Django request object in the definition lambda for the QuerySet). By providing a QuerySet that is already filtered by e.g., user account, the library will use that QuerySet in the resolvers it generates. The requirement that you must _remember_ to filter by account is all but eliminated.

It builds each relationship into the schema, so you can traverse from `Label` to `Artists` to `Albums` to `Songs` in a single query (both in the result-set and via filtering), still retrieving only the data you need.

You can specify arbitrarily complex SQL statements: the schema allows specifying filtering via `where`, `orderBy`, `offset`, `limit` clauses.

It allows smooth (nested, if you're bold enough!) updates & inserts.

Perhaps best of all, it automatically generates `select_related` and `prefetch_related` calls to your QuerySet. This avoids the classic GraphQL N+1 problem usually solved by things like [dataloader](https://docs.graphene-python.org/en/latest/execution/dataloader/). Additionally, it fetches _only_ the columns necessary to satisfy the query. No over fetching!

A hand-rolled schema providing all of this for a single model would be hundreds of lines of code. Multiply that by a realistic, mature application with a hundred or more models, and you have an unmaintainable mess. This library auto-generates it for you, leaving the "fun" stuff for you.
