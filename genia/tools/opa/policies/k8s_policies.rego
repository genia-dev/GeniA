package policy

deny[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("Container '%v' runs as root", [container.name])
}

deny[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.resources.limits.cpu
    not container.resources.limits.memory
    msg := sprintf("Container '%v' does not have CPU and memory limits defined", [container.name])
}
