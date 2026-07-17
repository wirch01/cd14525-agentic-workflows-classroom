# Agentic Workflow Flowchart

```mermaid
flowchart TD
    Start([Start Workflow]) --> Spec[/Load Product Spec<br/>Product-Spec-Email-Router.txt/]
    Spec --> Prompt[/"Workflow Prompt:<br/>What would the development<br/>tasks for this product be?"/]

    Prompt --> APA[Action Planning Agent<br/>extract_steps_from_prompt]
    APA --> Steps[/Ordered list of<br/>workflow steps/]

    Steps --> Loop{{For each step}}
    Loop --> Router[Routing Agent<br/>route step to best agent<br/>via semantic similarity]

    Router -->|Persona / user story step| PM_SF[product_manager_support_function]
    Router -->|Feature grouping step| PGM_SF[program_manager_support_function]
    Router -->|Engineering task step| DE_SF[development_engineer_support_function]

    subgraph PM [Product Manager]
        PM_SF --> PM_K[Knowledge Augmented<br/>Prompt Agent - respond]
        PM_K --> PM_E[Evaluation Agent<br/>validate user stories]
        PM_E -->|not valid, retry<br/>up to max_interactions| PM_K
        PM_E -->|valid| PM_Out[/Validated response/]
    end

    subgraph PGM [Program Manager]
        PGM_SF --> PGM_K[Knowledge Augmented<br/>Prompt Agent - respond]
        PGM_K --> PGM_E[Evaluation Agent<br/>validate features]
        PGM_E -->|not valid, retry<br/>up to max_interactions| PGM_K
        PGM_E -->|valid| PGM_Out[/Validated response/]
    end

    subgraph DE [Development Engineer]
        DE_SF --> DE_K[Knowledge Augmented<br/>Prompt Agent - respond]
        DE_K --> DE_E[Evaluation Agent<br/>validate tasks]
        DE_E -->|not valid, retry<br/>up to max_interactions| DE_K
        DE_E -->|valid| DE_Out[/Validated response/]
    end

    PM_Out --> Collect[Append result to<br/>completed_steps]
    PGM_Out --> Collect
    DE_Out --> Collect

    Collect --> More{More steps?}
    More -->|Yes| Loop
    More -->|No| Final[/Print final output:<br/>last completed step/]
    Final --> End([End Workflow])
```
