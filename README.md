# i-rars-api

Example:
```bash
curl http://127.0.0.1:5000/api/recommender -d "api-key=123456&title=XMapDB-sim: Performance evalaution on model-based XML to relational database mapping choices"
```

Return:
```json
[
    {
        "a": {
            "@seq": "2",
            "emailAddress": "aldo.vw@ufsc.br",
            "@_fa": "true",
            "surname": "Von Wangenheim",
            "initials": "A.",
            "authname": "Von Wangenheim A.",
            "given-name": "Aldo",
            "author-url": "https://api.elsevier.com/content/author/author_id/6602002506",
            "afid": "[{\"@_fa\": \"true\", \"$\": \"60017609\"}]",
            "authid": "6602002506"
        }
    },
    {
        "a": {
            "@seq": "1",
            "emailAddress": "douglas.macedo@ufsc.br",
            "@_fa": "true",
            "surname": "De Macedo",
            "initials": "D.D.J.",
            "authname": "De Macedo D.",
            "given-name": "Douglas D.J.",
            "author-url": "https://api.elsevier.com/content/author/author_id/24823749200",
            "authid": "24823749200"
        }
    },
    {
        "a": {
            "@seq": "3",
            "emailAddress": "mario.dantas@ice.ufjf.br",
            "@_fa": "true",
            "surname": "Dantas",
            "initials": "M.A.R.",
            "authname": "Dantas M.",
            "given-name": "Mario A.R.",
            "author-url": "https://api.elsevier.com/content/author/author_id/9744594600",
            "afid": "[{\"@_fa\": \"true\", \"$\": \"60017609\"}]",
            "authid": "9744594600"
        }
    },
    {
        "a": {
            "@seq": "2",
            "emailAddress": "md.alshammari@uoh.edu.sa",
            "@_fa": "true",
            "surname": "Alshammari",
            "initials": "M.T.",
            "authname": "Alshammari M.T.",
            "given-name": "Mohammad T.",
            "author-url": "https://api.elsevier.com/content/author/author_id/56407071800",
            "afid": "[{\"@_fa\": \"true\", \"$\": \"60104671\"}]",
            "authid": "56407071800"
        }
    },
    {
        "a": {
            "@seq": "1",
            "emailAddress": "am.qtaish@uoh.edu.sa",
            "@_fa": "true",
            "surname": "Qtaish",
            "initials": "A.",
            "authname": "Qtaish A.",
            "orcid": "0000-0001-5210-7086",
            "given-name": "Amjad",
            "author-url": "https://api.elsevier.com/content/author/author_id/56720387400",
            "afid": "[{\"@_fa\": \"true\", \"$\": \"60001821\"}]",
            "authid": "56720387400"
        }
    }
]

```

