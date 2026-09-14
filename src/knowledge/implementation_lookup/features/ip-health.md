# IP / Health / Validity (implementation map)

Question example: does VPS to VPN check IP health/validity?

Answer policy: Implementation is source of truth. Do not say “not in catalog therefore no”.

| Capability | Code | Status |
|------------|------|--------|
| Probe Central IP + panel domain from this PC | `F:\VPS to VPN\internal\netcheck\reach.go` `ProbeCentralFromThisPC` | EXISTS |
| Diagnose verdict healthy | `internal\netcheck\diagnose.go` | EXISTS |
| Validate tunnel subnet / IP overlap | `internal\netcheck\ip.go` `ValidateNewTunnelSubnet` | EXISTS |
| Verify exit server / active link / central panel | `internal\health\health.go` `VerifyExitServer` `VerifyCentralPanel` `VerifyLocationDeploy` | EXISTS |
| Host check helper | `internal\netcheck\checkhost.go` | EXISTS |

Support Catalog may omit these IDs. Still report EXISTS from implementation.
