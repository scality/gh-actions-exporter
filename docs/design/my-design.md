- J'arrive pas à trouver comment afficher qqch dans l'onglet `Check` de la PR,
  en mode comme avec CodeQL ... Sachant que CodeQL n'upload que des SARIF, donc
  je vois pas comment faire (il y a peut-être une solution, je vais creuser)

- En attendant, il y a la solution de créer un commentaire à chaque fois qu'il
  y a un trigger de CI au niveau de la PR.
  **Problème 1** : plein de commentaires dans tous les sens -> Chiant, donc il
  faut ajouter des lignes de code pour supprimer et recréer un commentaire (ou
  le modifier)

```yaml
- name: Add comment to PR
uses: actions/github-script@v5
with:
    github-token: ${{secrets.GITHUB_TOKEN}}
    # Exemple
    script: |
        const { createPrometheusClient } = require('@promster/metrics');
        const client = createPrometheusClient({
            prometheusEndpoint: 'https://XXXXX',
        });
        const result = await client.getMetric('github_actions_job_cost_count_total', {
            job: '${{ github.job }}',
        });
        github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: '${result.metric.value}'
        })
```

- En fait on a pas forcément besoin d'utiliser Prometheus. Le truc c'est que si
  on utilise Prometheus, faudrait l'appeler à la fin du run et pas au début ou
  pendant, sinon Prometheus ne sera pas à jour. Donc pour ça 2 options : - On utilise Prometheus ainsi que des Webhooks, pour qu'à chaque fin de run
  ça appelle un programme qui met un commentaire en place sur la PR avec le coût
  que cela à engendré (j'ai pas encore vérifié la faisabilité)

      - On récupère la config qu'il y a et on fait le calcul nous-mêmes (c'est pas
      si ouf mais ça a l'air plus simple comme ça) -> Mais trop trop chiant parce
      que ça veut dire rajouter à chaque workflow ça, c'est relou

- Meilleur option :
  1. Webhook GitHub qui trigger une application tierce lorsqu'un Workflow de CI
     se finit -> `workflow_run` et `workflow_job`
  2. Le Webhook se déclenche à chaque fois qu'un `workflow_run` est complété
  3. Envoie une POST request à notre URL (avec plein d'info)
  4. Faire un script pour récupérer cette POST request avec toutes les infos,
     en déduire le coût grâce aux nouvelles data de Prometheus (auquel on
     fait un appel)
  5. Avec les infos récupérées précédemment grâce à la POST request, en déduire
     la PR correspondante :
     - Si commentaire pas présent : le créer et mettre que le dernier run a coûté
       tant
     - Si commentaire déjà présent : le modifier pour ajouter le coût du dernier
       run tout en gardant les coûts des précédents (en gros récupérer le contenu
       du commentaire et y ajouter une nouvelle dépense en bas). À voir pour calculer
       le total également

check_suite et check_run
Rien rajouté dans le workflow
On crée juste un webhook au niveau de l'organisation pour tout gérer

1. Webhook au niveau de l'org Scality avec appel workflow -> `workflow_run` et `workflow_job`
   (prendre le même webhook que Prometheus) -> OK
2. L'algo de la facture se déclenche à chaque fois qu'un `workflow_run` est complété ->

> GET à GitHub pour récupérer les `check_runs` / `workflow_job` ... qui appartiennent aux
> `workflow_run` reçu. Possible que ça se fasse avec cette API mais à voir
> Tu calcules le coût de ce `workflow_run`
> Checker si y'a déjà un ticket de caisse
> Soit en créer un, y mettre le prix + total (même chose du coup) du run
> Soit tu récupères les infos, tu récupères l'ancien texte, t'y ajoutes le nouveau
> Tu balances le `string` que t'a dans l'onglet `check` de GitHub (maybe aussi en commentaire)
> avec une requête qui tape sur Github -> Request POST

Étape 1a: List check runs for a Git reference
$ gh api \
 -H "Accept: application/vnd.github+json" \
 -H "X-GitHub-Api-Version: 2022-11-28" \
 /repos/scalanga-devl/runners-test/commits/4a43b9a/check-runs

> check_runs[0].id = 11681039521

Étape 1b: Get a check run
$ gh api \
 -H "Accept: application/vnd.github+json" \
 -H "X-GitHub-Api-Version: 2022-11-28" \
 /repos/scalanga-devl/runners-test/check-runs/11681039521

> Fais la même chose mais avec juste un check-run et pas tous

~ curl -L \
 -X POST \
 -H "Accept: application/vnd.github+json" \
 -H "Authorization: Bearer ghp_XXXXXX"\
 -H "X-GitHub-Api-Version: 2022-11-28" \
 https://api.github.com/repos/scalanga-devl/runners-test/check-runs \
 -d '{"name":"mighty_readme","head_sha":"008a6959532321fb621712cca91b875ef896f75d","status":"in_progress","external_id":"42","started_at":"2018-05-04T01:14:52Z","output":{"title":"Mighty Readme report","summary":"","text":""}}'
{
"message": "You must authenticate via a GitHub App.",
"documentation_url": "https://docs.github.com/rest/reference/checks#create-a-check-run"
}

```bash
gh api \
--method POST \
-H "Accept: application/vnd.github+json" \
-H "X-GitHub-Api-Version: 2022-11-28" \
/repos/scalanga-devl/runners-test/check-suites \
-F name="mighty_readme" \
-F head_sha="008a6959532321fb621712cca91b875ef896f75d"
```

-> Erreur

```bash
~ gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/scalanga-devl/runners-test/check-suites \
  -f head_sha='008a6959532321fb621712cca91b875ef896f75d'
{
  "message": "Not Found",
  "documentation_url": "https://docs.github.com/rest/reference/checks#create-a-check-suite"
}
```

```yaml
#!/usr/bin/env python3
import jwt
import time
import sys

# Get PEM file path
if len(sys.argv) > 1:
    pem = sys.argv[1]
else:
    pem = input("Enter path of private PEM file: ")

# Get the App ID
if len(sys.argv) > 2:
    app_id = sys.argv[2]
else:
    app_id = input("Enter your APP ID: ")

# Open PEM
with open(pem, 'rb') as pem_file:
    signing_key = jwt.jwk_from_pem(pem_file.read())

payload = {
    # Issued at time
    'iat': int(time.time()),
    # JWT expiration time (10 minutes maximum)
    'exp': int(time.time()) + 600,
    # GitHub App's identifier
    'iss': app_id
}

# Create JWT
jwt_instance = jwt.JWT()
encoded_jwt = jwt_instance.encode(payload, signing_key, alg='RS256')

print(f"JWT:  {encoded_jwt}")
```

-> Get an `encoded_jwt` token from a GitHub Apps : https://github.com/organizations/scalanga-devl/settings/apps -> Install App -> Get the Installer token from the URL : 37050127

```bash
~ curl --request POST \
--url "https://api.github.com/app/installations/37050127/access_tokens" \
--header "Accept: application/vnd.github+json" \
--header "Authorization: Bearer XXXXX(giga long, jwt token)" \
--header "X-GitHub-Api-Version: 2022-11-28"
```

-> Then we're getting a token : ghs_XXX

```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  --header "Authorization: Bearer ghs_XXX" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/scalanga-devl/runners-test/check-suites \
  -d '{"head_sha":"4a43b9ab28360192129a6c7ff192b921b22f8837"}'
```

-> It works !!!

```bash
~ python3 test.py
Enter path of private PEM file: Downloads/check-suites.2023-05-01.private-key.pem
Enter your APP ID: 326408
JWT:  XXXXXXX
```

```bash
~ curl --request POST \
--url "https://api.github.com/app/installations/37050127/access_tokens" \
--header "Accept: application/vnd.github+json" \
--header "Authorization: Bearer XXXX" \
--header "X-GitHub-Api-Version: 2022-11-28"
```

-> token = ghs_XXXX

```bash
curl -L \
-X POST \
-H "Accept: application/vnd.github+json" \
-H "Authorization: Bearer ghs_XXX"\
-H "X-GitHub-Api-Version: 2022-11-28" \
https://api.github.com/repos/scalanga-devl/runners-test/check-runs \
-d '{"name":"test3","head_sha":"4a43b9ab28360192129a6c7ff192b921b22f8837","status":"queued","external_id":"42","started_at":"2018-05-04T01:14:52Z","output":{"title":"Mighty Readme report","summary":"","text":""}}'
```

-> It's works
(It create a check-suites by itself)
(If you give the same name it will delete the past one a create a new one)

```bash
curl -L \
-H "Accept: application/vnd.github+json" \
-H "Authorization: Bearer ghs_XXX"\
-H "X-GitHub-Api-Version: 2022-11-28" \
https://api.github.com/repos/scalanga-devl/runners-test/check-runs/13157937534
```

-> output.text = "1st CI run: 20.43$.\n2nd CI run: 19.54$."

Take this and do :

```bash
curl -L \
-X POST \
-H "Accept: application/vnd.github+json" \
-H "Authorization: Bearer ghs_XXX"\
-H "X-GitHub-Api-Version: 2022-11-28" \
https://api.github.com/repos/scalanga-devl/runners-test/check-runs \
-d '{"name":"Price","head_sha":"4a43b9ab28360192129a6c7ff192b921b22f8837","status":"completed","details_url":"https://docs.github.com/en/rest/checks/suites?apiVersion=2022-11-28#create-a-check-suite","conclusion":"success","output":{"title":"Price of CI run(s)","summary":"Behind a CI run, there are servers running which cost money, so it is important to be careful not to abuse this feature to avoid wasting money",

"text":"${output.text} \n newText ..."}}'

```

What we need :

- `"head_sha":"4a43b9ab28360192129a6c7ff192b921b22f8837"`
- `text`
- Bearer token
  - JWT token
    - private PEM file
    - APP ID

`View more details on check-suites` -> À voir comment le modifier ou l'enlever !

JS Code that works :

```javascript
const { Octokit } = require("@octokit/rest");

const octokit = new Octokit({
  auth: "ghs_XXXX",
});

const createCheck = async () => {
  const owner = "scalanga-devl";
  const repo = "runners-test";

  try {
    const response = await octokit.checks.create({
      owner,
      repo,
      name: "My Check",
      head_sha: "4a43b9ab28360192129a6c7ff192b921b22f8837",
      status: "completed",
      conclusion: "success",
      output: {
        title: "My Check Results",
        summary: "All checks passed successfully!",
      },
    });

    console.log(`Check run created: ${response.data.html_url}`);
  } catch (error) {
    console.error(error);
  }
};
```

Python Code that works :

```py
import os
from github import Github

token = 'ghs_XXX'
g = Github(login_or_token=token)

def create_check():
        repo = g.get_repo("scalanga-devl/runners-test")
        sha = "4a43b9ab28360192129a6c7ff192b921b22f8837"

        check_run = repo.create_check_run(
            name="My Check2",
            head_sha=sha,
            status="completed",
            conclusion="success",
            output={
                "title": "My Check Results",
                "summary": "All checks passed successfully!"
            }
        )

        print(f"Check run created: {check_run.html_url}")

create_check()
```

Python Get Method :

```py
import os
from github import Github

token: str = 'ghs_XXXXXX'
g: Github = Github(login_or_token=token)

def get_check_run():
    repo = g.get_repo("scalanga-devl/runners-test")
    sha: str = "4a43b9ab28360192129a6c7ff192b921b22f8837"

    check_run = repo.get_check_run(13177380724)

    print(check_run.output.text)

get_check_run()
```

# Simulation

## Step 1: Get the JWT token

```bash
Enter path of private PEM file: Downloads/check-suites.2023-05-01.private-key.pem
Enter your APP ID: 326408
```

-> JWT: XXXXXXXXXXXXXXX

## Step 2: Get the bearer token

```bash
curl --request POST \
--url "https://api.github.com/app/installations/37050127/access_tokens" \
--header "Accept: application/vnd.github+json" \
--header "Authorization: Bearer XXXXXXXXX" \
--header "X-GitHub-Api-Version: 2022-11-28"
```

-> ghs_XXXXXXX

## Step 3a: When a workflow is triggered and mark as `workflow_run.completed`, check if the check_run is already created

```bash
gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/scalanga-devl/runners-test/commits/063eec46348ff57a9982e70dfdb312c4262962bd/check-runs?check_name=Cost
```

**(Problem with the `check_name` parameter)**

## Step 3b: If the check-runs already exist, get the `output.test` variable and store it

## Step 4: Create / Modify the check-run "Cost"

```py
from github import Github

token: str = 'ghs_XXXXXX'
g: Github = Github(login_or_token=token)

def create_check():
        repo = g.get_repo("scalanga-devl/runners-test")
        sha: str = "063eec46348ff57a9982e70dfdb312c4262962bd"
        text: str = "CI run n.1: " + cost + "$"
        # Maybe use `output.test` if the `check-runs`
        # "1st CI run: 20.43$.\n2nd CI run: 19.54$."

        check_run = repo.create_check_run(
            name="Cost",
            head_sha=sha,
            status="completed",
            conclusion="success",
            output={
                "title": "Cost",
                "summary": "Behind a CI run, there are servers running which cost money, so it is important to be careful not to abuse this feature to avoid wasting money.",
                "text": text
            }
        )

        print(f"Check run created: {check_run.html_url}")

create_check()
```

```bash
gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/scalanga-devl/runners-test/actions/runs/4863427856/jobs
```

-> Pour lister les `workflow_job` à partir d'un `workflow_run`
