# Agent Category Theory

[![CI](https://github.com/Kubo-cmd/agent-category-theory/actions/workflows/ci.yml/badge.svg)](https://github.com/Kubo-cmd/agent-category-theory/actions/workflows/ci.yml)

Mathematical framework for composing agent behaviors using category theory — the "mathematics of mathematics."

## The Problem

Agent systems are built from composable transformations:
- State transitions (idle → thinking → acting → done)
- Data pipelines (input → process → output)
- Side effects (memory, I/O, errors)

But composition is ad-hoc. We need a **universal algebra of composition**.

Category theory provides this. It's the most abstract framework humans have created for understanding structure, composition, and transformation.

## Core Concepts

### Objects and Morphisms

```python
from agent_category_theory import Object, Morphism

# Objects are agent states
idle = Object("Idle")
thinking = Object("Thinking")
acting = Object("Acting")

# Morphisms are transformations
start_thinking = Morphism(idle, thinking, lambda x: f"{x} → thinking")
start_acting = Morphism(thinking, acting, lambda x: f"{x} → acting")

# Compose them in execution order: first thinking, then acting
lifecycle = start_thinking.compose(start_acting)
print(lifecycle("agent"))  # "agent → thinking → acting"
```

### Identity and Composition Laws

Every category must satisfy:
- **Identity**: `f ∘ id = f = id ∘ f`
- **Associativity**: `(f ∘ g) ∘ h = f ∘ (g ∘ h)`

```python
from agent_category_theory import Identity

id_idle = Identity(idle)
left_identity = id_idle.compose(start_thinking)
right_identity = start_thinking.compose(Identity(thinking))
assert left_identity("agent") == start_thinking("agent")
assert right_identity("agent") == start_thinking("agent")
```

### Agent Categories

```python
from agent_category_theory import AgentCategory

cat = AgentCategory("AgentLifecycle")
cat.add_morphism(start_thinking)
cat.add_morphism(start_acting)

print(cat)  # AgentCategory(AgentLifecycle, 3 objects, 2 morphisms)
```

### Functors: Structure-Preserving Mappings Between Categories

Functors preserve structure when mapping between categories.

```python
from agent_category_theory import Functor

class SuffixFunctor(Functor):
    def map_object(self, obj):
        return Object(f"{obj.name}_mapped")
    
    def map_morphism(self, morph):
        return Morphism(
            self.map_object(morph.source),
            self.map_object(morph.target),
            morph.func
        )

F = SuffixFunctor()
mapped = F.map_object(idle)  # Object("Idle_mapped")
```

Concrete subclasses are responsible for preserving identities and composition.

### Monads: Encapsulating Side Effects

Monads handle side effects (memory, errors, I/O) in a composable way.

#### Memory Monad

Accumulates memory across computations:

```python
from agent_category_theory import MemoryMonad

mem = MemoryMonad("initial", [])
mem = mem.store("fact1")
mem = mem.store("fact2")

print(mem.recall())  # ["fact1", "fact2"]
```

#### Maybe Monad

Handles computations that might fail:

```python
from agent_category_theory import MaybeMonad

just = MaybeMonad(42)
nothing = MaybeMonad(None)

result = just.bind(lambda x: MaybeMonad(x * 2))
print(result.value)  # 84

result = nothing.bind(lambda x: MaybeMonad(x * 2))
print(result.value)  # None
```

## Why This Matters

1. **Structured composition**: Morphisms compose in checked source-to-target order
2. **Universal patterns**: Functors, monads, natural transformations appear everywhere
3. **Side-effect management**: Monads isolate memory, errors, I/O
4. **Verification**: Tests can check category laws extensionally for concrete morphisms
5. **Abstraction**: Same patterns work for agents, databases, UIs, networks

## Installation

```bash
git clone https://github.com/Kubo-cmd/agent-category-theory.git
cd agent-category-theory
python -m pip install .
```

The library has no runtime dependencies and supports Python 3.9 or newer.

## Usage

```bash
python agent_category_theory.py
```

## Tests

```bash
python -m pip install ".[test]"
python -m pytest -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete local verification flow
and [SECURITY.md](SECURITY.md) for private vulnerability reporting.

## License

MIT

## Related

- [agent-memory-topology](https://github.com/Kubo-cmd/agent-memory-topology) — Persistent homology
- [agent-wasserstein-geometry](https://github.com/Kubo-cmd/agent-wasserstein-geometry) — Optimal transport
- [agent-information-geometry](https://github.com/Kubo-cmd/agent-information-geometry) — Fisher information

## Agent Math Series

Part of a 10-repo series applying advanced mathematics to agent systems:

- [agent-lie-groups](https://github.com/Kubo-cmd/agent-lie-groups) — Continuous symmetry
- [agent-knot-theory](https://github.com/Kubo-cmd/agent-knot-theory) — Entanglement invariants
- [agent-tqft](https://github.com/Kubo-cmd/agent-tqft) — Topological quantum field theory
- [agent-operad-theory](https://github.com/Kubo-cmd/agent-operad-theory) — Multi-input composition
- [agent-homotopy-type-theory](https://github.com/Kubo-cmd/agent-homotopy-type-theory) — Identity types
- [agent-topos-theory](https://github.com/Kubo-cmd/agent-topos-theory) — Logic and geometry
- [agent-sheaf-theory](https://github.com/Kubo-cmd/agent-sheaf-theory) — Local-to-global data
- [agent-representation-theory](https://github.com/Kubo-cmd/agent-representation-theory) — Symmetry representations
- [agent-information-geometry](https://github.com/Kubo-cmd/agent-information-geometry) — Fisher information
- [agent-memory-topology](https://github.com/Kubo-cmd/agent-memory-topology) — Persistent homology
- [agent-wasserstein-geometry](https://github.com/Kubo-cmd/agent-wasserstein-geometry) — Optimal transport
