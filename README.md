# Agent Category Theory

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

# Compose them
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
assert start_thinking.compose(id_idle) == start_thinking
```

### Agent Categories

```python
from agent_category_theory import AgentCategory

cat = AgentCategory("AgentLifecycle")
cat.add_morphism(start_thinking)
cat.add_morphism(start_acting)

print(cat)  # AgentCategory(AgentLifecycle, 3 objects, 2 morphisms)
```

### Functors: Mappings Between Categories

Functors preserve structure when mapping between categories.

```python
from agent_category_theory import Functor

class DoubleFunctor(Functor):
    def map_object(self, obj):
        return Object(f"{obj.name}_doubled")
    
    def map_morphism(self, morph):
        return Morphism(
            self.map_object(morph.source),
            self.map_object(morph.target),
            lambda x: morph(x) * 2
        )

F = DoubleFunctor()
mapped = F.map_object(idle)  # Object("Idle_doubled")
```

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

1. **Formal composition**: Morphisms compose associatively with identity — guaranteed correct pipelines
2. **Universal patterns**: Functors, monads, natural transformations appear everywhere
3. **Side-effect management**: Monads isolate memory, errors, I/O
4. **Verification**: Category laws enable formal proof of correctness
5. **Abstraction**: Same patterns work for agents, databases, UIs, networks

## Installation

```bash
pip install numpy  # Only dependency
```

## Usage

```bash
python agent_category_theory.py
```

## Tests

```bash
pytest tests/ -v
```

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
