    # 0003: disable auto deploy on render

    ## Context
    By default the auto deploy setting is set on commit, so whenever you push your code to the main branch the application will auto deploy.

    ## Decision
    Change auto deploy setting to "After CI Checks Pass" option to only deploy if the GitHub Actions status for the commit succeeded.

    ## Alternative
    - Deploy Hook: turn auto deploy off and trigger a deployment via HTTP Request manually

    ## Consequences
    Deployments are now triggered on CI success, preventing broken code from reaching production