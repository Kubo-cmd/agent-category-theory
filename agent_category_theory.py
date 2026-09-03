#!/usr/bin/env python3
"""
Agent Category Theory — Mathematical framework for composing agent behaviors.

Category theory is the "mathematics of mathematics" — the most abstract framework
for understanding structure, composition, and transformation.

Applied to agents:
- Objects = agent states
- Morphisms = agent transformations
- Composition = chaining behaviors
- Functors = mappings between agent categories
- Natural transformations = transformations between functors
- Monads = encapsulating side effects (memory, I/O)

This repo provides the categorical primitives for building composable agent systems.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar
from abc import ABC, abstractmethod


# Type variables
A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')



# =============================================================================
# Category: Objects and Morphisms
# =============================================================================

@dataclass(frozen=True)
class Object:
    """An object in a category (an agent state)."""
    name: str
    
    def __repr__(self):
        return f"Object({self.name})"


class Morphism(ABC, Generic[A, B]):
    """A morphism (transformation) from object A to object B."""
    
    def __init__(self, source: Object, target: Object, func: Callable[[A], B]):
        self.source = source
        self.target = target
        self.func = func
    
    def __call__(self, x: A) -> B:
        """Apply the morphism."""
        return self.func(x)
    
    def compose(self, other: 'Morphism[B, C]') -> 'Morphism[A, C]':
        """Apply this morphism, then ``other``."""
        if self.target != other.source:
            raise ValueError(
                f"Cannot compose: {self.target} != {other.source}"
            )
        
        composed_func = lambda x: other(self(x))
        return Morphism(self.source, other.target, composed_func)
    
    def __repr__(self):
        return f"Morphism({self.source} → {self.target})"


class Identity(Morphism[A, A]):
    """Identity morphism: id_A : A → A."""
    
    def __init__(self, obj: Object):
        super().__init__(obj, obj, lambda x: x)
    
    def __repr__(self):
        return f"Identity({self.source})"


# =============================================================================
# Functor: Mapping between categories
# =============================================================================

class Functor(ABC, Generic[A, B]):
    """Map objects and morphisms; subclasses must preserve category laws."""
    
    @abstractmethod
    def map_object(self, obj: Object) -> Object:
        """Map an object."""
        raise NotImplementedError
    
    @abstractmethod
    def map_morphism(self, morphism: Morphism) -> Morphism:
        """Map a morphism."""
        raise NotImplementedError
    
    def __call__(self, x: Any) -> Any:
        """Apply the functor to an object or morphism."""
        if isinstance(x, Object):
            return self.map_object(x)
        elif isinstance(x, Morphism):
            return self.map_morphism(x)
        else:
            raise TypeError(f"Cannot apply functor to {type(x)}")


# =============================================================================
# Natural Transformation: Transformation between functors
# =============================================================================

@dataclass
class NaturalTransformation:
    """Components between functors with validated endpoints.

    Construction checks each component has type ``F(X) -> G(X)``. General
    naturality requires equality over user-defined callables, so callers remain
    responsible for checking the naturality square in their concrete domain.
    """
    name: str
    source_functor: Functor
    target_functor: Functor
    components: Dict[Object, Morphism]  # Object → Morphism

    def __post_init__(self) -> None:
        for obj, component in self.components.items():
            if not isinstance(obj, Object) or not isinstance(component, Morphism):
                raise TypeError("Components must map Object values to Morphism values")
            expected_source = self.source_functor.map_object(obj)
            expected_target = self.target_functor.map_object(obj)
            if component.source != expected_source or component.target != expected_target:
                raise ValueError(
                    f"Invalid component for {obj}: expected "
                    f"{expected_source} -> {expected_target}, got "
                    f"{component.source} -> {component.target}"
                )
    
    def component(self, obj: Object) -> Morphism:
        """Get the component at object X: η_X : F(X) → G(X)."""
        if obj not in self.components:
            raise KeyError(f"No component for {obj}")
        return self.components[obj]
    
    def __repr__(self):
        return f"NaturalTransformation({self.name})"


# =============================================================================
# Monad: Encapsulating side effects
# =============================================================================

class Monad(ABC, Generic[A]):
    """A monad encapsulates computations with side effects."""
    
    @abstractmethod
    def unit(self, value: A) -> 'Monad[A]':
        """Wrap a value (return/pure)."""
        raise NotImplementedError
    
    @abstractmethod
    def bind(self, f: Callable[[A], 'Monad[B]']) -> 'Monad[B]':
        """Chain computations (>>= / flatMap)."""
        raise NotImplementedError
    
    def map(self, f: Callable[[A], B]) -> 'Monad[B]':
        """Apply a function inside the monad (fmap)."""
        return self.bind(lambda x: self.unit(f(x)))


@dataclass
class MemoryMonad(Monad[A]):
    """Monad for agent memory operations."""
    value: A
    memory_state: List[Any]
    
    def unit(self, value: A) -> 'MemoryMonad[A]':
        return MemoryMonad(value, [])
    
    def bind(self, f: Callable[[A], 'MemoryMonad[B]']) -> 'MemoryMonad[B]':
        result = f(self.value)
        # Accumulate memory
        new_memory = self.memory_state + result.memory_state
        return MemoryMonad(result.value, new_memory)
    
    def store(self, item: Any) -> 'MemoryMonad[A]':
        """Store an item in memory."""
        return MemoryMonad(self.value, self.memory_state + [item])
    
    def recall(self) -> List[Any]:
        """Recall all stored items."""
        return self.memory_state.copy()
    
    def __repr__(self):
        return f"MemoryMonad(value={self.value}, memory={self.memory_state})"


@dataclass
class MaybeMonad(Monad[A]):
    """Monad for computations that might fail."""
    value: Optional[A]
    
    def unit(self, value: A) -> 'MaybeMonad[A]':
        return MaybeMonad(value)
    
    def bind(self, f: Callable[[A], 'MaybeMonad[B]']) -> 'MaybeMonad[B]':
        if self.value is None:
            return MaybeMonad(None)
        return f(self.value)
    
    def is_just(self) -> bool:
        return self.value is not None
    
    def is_nothing(self) -> bool:
        return self.value is None
    
    def __repr__(self):
        return f"MaybeMonad({self.value})"


# =============================================================================
# Agent Category: Concrete application
# =============================================================================

class AgentCategory:
    """A category of agent states and transformations."""
    
    def __init__(self, name: str):
        self.name = name
        self.objects: List[Object] = []
        self.morphisms: List[Morphism] = []
    
    def add_object(self, obj: Object):
        """Add an object (agent state) to the category."""
        if obj not in self.objects:
            self.objects.append(obj)
    
    def add_morphism(self, morphism: Morphism):
        """Add a morphism (transformation) to the category."""
        self.morphisms.append(morphism)
        # Ensure source and target are in the category
        if morphism.source not in self.objects:
            self.objects.append(morphism.source)
        if morphism.target not in self.objects:
            self.objects.append(morphism.target)
    
    def compose_chain(self, morphisms: List[Morphism]) -> Morphism:
        """Compose a chain of morphisms: f_n ∘ ... ∘ f_2 ∘ f_1."""
        if not morphisms:
            raise ValueError("Cannot compose empty chain")
        
        result = morphisms[0]
        for m in morphisms[1:]:
            result = result.compose(m)
        
        return result
    
    def identity(self, obj: Object) -> Identity:
        """Get the identity morphism for an object."""
        if obj not in self.objects:
            raise ValueError(f"{obj} not in category")
        return Identity(obj)
    
    def __repr__(self):
        return f"AgentCategory({self.name}, {len(self.objects)} objects, {len(self.morphisms)} morphisms)"


# =============================================================================
# Yoneda Lemma: Universal property
# =============================================================================

class YonedaEmbedding:
    """The Yoneda embedding: embeds objects into functor category."""
    
    def __init__(self, category: AgentCategory):
        self.category = category
    
    def embed(self, obj: Object) -> Callable[[Morphism], Any]:
        """Return a membership-filtered evaluator for ``Hom(-, obj)``."""
        if obj not in self.category.objects:
            raise ValueError(f"{obj} not in category")

        def hom_set(morphism: Morphism) -> Any:
            if morphism in self.category.morphisms and morphism.target == obj:
                return morphism
            return None
        
        return hom_set


# =============================================================================
# Demo
# =============================================================================

def main():
    """Demonstrate category theory for agents."""
    print("=" * 70)
    print("Agent Category Theory — Demonstration")
    print("=" * 70)
    print()
    
    # Create agent states (objects)
    idle = Object("Idle")
    thinking = Object("Thinking")
    acting = Object("Acting")
    done = Object("Done")
    
    print("Agent states (objects):")
    print(f"  {idle}")
    print(f"  {thinking}")
    print(f"  {acting}")
    print(f"  {done}")
    print()
    
    # Create transformations (morphisms)
    start_thinking = Morphism(idle, thinking, lambda x: f"{x} → thinking")
    start_acting = Morphism(thinking, acting, lambda x: f"{x} → acting")
    finish = Morphism(acting, done, lambda x: f"{x} → done")
    
    print("Transformations (morphisms):")
    print(f"  {start_thinking}")
    print(f"  {start_acting}")
    print(f"  {finish}")
    print()
    
    # Compose morphisms
    agent_lifecycle = start_thinking.compose(start_acting).compose(finish)
    print(f"Composed lifecycle: {agent_lifecycle}")
    print(f"Applied: {agent_lifecycle('agent')}")
    print()
    
    # Identity morphism
    id_idle = Identity(idle)
    print(f"Identity: {id_idle}")
    print(f"Applied: {id_idle('agent')}")
    print()
    
    # Agent category
    cat = AgentCategory("AgentLifecycle")
    cat.add_morphism(start_thinking)
    cat.add_morphism(start_acting)
    cat.add_morphism(finish)
    print(f"Category: {cat}")
    print()
    
    # Memory monad
    print("Memory Monad:")
    mem = MemoryMonad("initial", [])
    mem = mem.store("fact1")
    mem = mem.store("fact2")
    print(f"  {mem}")
    print(f"  Recalled: {mem.recall()}")
    print()
    
    # Maybe monad
    print("Maybe Monad:")
    just = MaybeMonad(42)
    nothing = MaybeMonad(None)
    print(f"  Just: {just}")
    print(f"  Nothing: {nothing}")
    print(f"  Just.is_just(): {just.is_just()}")
    print(f"  Nothing.is_nothing(): {nothing.is_nothing()}")
    print()
    
    # Functor example
    print("Functor (renaming):")
    class RenamingFunctor(Functor):
        def map_object(self, obj: Object) -> Object:
            return Object(f"mapped_{obj.name}")
        
        def map_morphism(self, morphism: Morphism) -> Morphism:
            return Morphism(
                self.map_object(morphism.source),
                self.map_object(morphism.target),
                morphism.func
            )
    
    rename = RenamingFunctor()
    print(f"  Object: {idle} → {rename.map_object(idle)}")
    print()
    
    print("=" * 70)
    print("Category theory provides the mathematical foundation for:")
    print("  • Composable agent behaviors")
    print("  • Formal verification of agent transformations")
    print("  • Universal patterns across different agent architectures")
    print("  • Side-effect management via monads")
    print("=" * 70)


if __name__ == "__main__":
    main()
