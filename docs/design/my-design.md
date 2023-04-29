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
pendant, sinon Prometheus ne sera pas à jour. Donc pour ça 2 options :
    - On utilise Prometheus ainsi que des Webhooks, pour qu'à chaque fin de run
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
`workflow_run` reçu. Possible que ça se fasse avec cette API mais à voir
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
  -H "Authorization: Bearer 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"\
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/scalanga-devl/runners-test/check-runs \
  -d '{"name":"mighty_readme","head_sha":"008a6959532321fb621712cca91b875ef896f75d","status":"in_progress","external_id":"42","started_at":"2018-05-04T01:14:52Z","output":{"title":"Mighty Readme report","summary":"","text":""}}'
{
  "message": "You must authenticate via a GitHub App.",
  "documentation_url": "https://docs.github.com/rest/reference/checks#create-a-check-run"
}


gh api \
--method POST \
-H "Accept: application/vnd.github+json" \
-H "X-GitHub-Api-Version: 2022-11-28" \
/repos/scalanga-devl/runners-test/check-suites \
-F name="mighty_readme" \
-F head_sha="008a6959532321fb621712cca91b875ef896f75d"
-> Erreur


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


