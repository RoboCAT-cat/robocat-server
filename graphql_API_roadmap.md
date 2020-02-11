# GraphQL API roadmap

An alternative roadmap for a GraphQL API in case it is deemed easier to implement.

It is divided on several stages, to let the frontend be developed alongside the backend.

API progress is shown as a GraphQL pseudo-schema.

## Stage 1 -- MVP

```graphql
type Category {
    id: String!
    name: String
    colour: String
    teams: [Team!]
}

type Team {
    id: String!
    category: Category
    name: String
    institution_name: String
    contact_info: String
}

type PartialScore {
    disqualified: Boolean
    stalled: Boolean
    cubesOnLowerGoal: Int
    cubesOnUpperGoal: Int
    cubesOnField: Int
    adhoc: Int
    notes: String
}

enum ScoreResult {
    WHITE_WON
    BLACK_WON
    DRAW
    BOTH_LOSE
}

type Score {
    whiteDisqualified: Boolean
    blackDisqualified: Boolean
    
    whiteStalled: Boolean
    blackStalled: Boolean

    cubesOnLowerWhite: Int
    cubesOnLowerBlack: Int

    cubesOnUpperWhite: Int
    cubesOnUpperBlack: Int

    cubesOnWhiteField: Int
    cubesOnBlackField: Int

    whiteAdhoc: Int
    blackAdhoc: Int

    notes: String

    # Calculated:
    whiteSum: Int
    blackSum: Int

    whiteQualificationPoints: Int
    blackQualificationPoints: Int

    result: ScoreResult
}

enum MatchStatus {
    NOT_PLAYED
    PLAYING
    SCORING
    FINISHED
}

type Match {
    id: Id

    white_team: Team
    black_team: Team

    status: MatchStatus

    partialWhiteScore: PartialScore
    partialBlackScore: PartialScore

    score: Score
}

type Query {
    allCategories: [Category!]
    category(categoryId: CategoryId!): Category
    allTeams: [Team!]
    team(teamId: String!): Team
    allMatches: [Match!]
    match(matchId: Id!): Match
}

schema {
    query: Query
}
```

## Stage 2 -- Interactive scoring

```graphql
type Query {
    # ...
    currentMatch: Match # Maybe?
}

type Mutation {
    scoreTeam(matchId: Id!, teamId: Id!, score: PartialScore): Match

    setMatchStatus(matchId: Id!, teamId: Id!, status: MatchStatus!): Match
}

schema {
    query: Query
    mutation: Mutation
}
```

## Stage 3 -- Scheduling

> Not yet defined

## Stage 4 -- Front-end admin

> Not yet defined
