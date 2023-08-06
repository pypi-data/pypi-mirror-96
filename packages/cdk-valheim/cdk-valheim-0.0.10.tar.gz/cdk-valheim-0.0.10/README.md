# cdk-valheim

A high level CDK construct of [Valheim](https://www.valheimgame.com/) dedicated server.

## API

See [API.md](API.md)

## Example

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
ValheimWorld(stack, "ValheimWorld",
    cpu=2048,
    memory_limit_mi_b=4096,
    schedules=[{
        "start_at": {"hour": "12", "week_day": "0-3"},
        "stop_at": {"hour": "1", "week_day": "0-3"}
    }],
    environment={
        "SERVER_NAME": "CDK Valheim",
        "WORLD_NAME": "Amazon",
        "SERVER_PASS": "fargate",
        "BACKUPS": "false"
    }
)
```

## Testing

* Snapshot

```sh
npx projen test
```

* Integration

```sh
npx cdk -a "npx ts-node src/integ.valheim.ts" diff
npx cdk -a "npx ts-node src/integ.valheim.ts" deploy
```
