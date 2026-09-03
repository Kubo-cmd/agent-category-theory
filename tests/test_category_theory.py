"""Tests for agent category theory."""

import pytest
from agent_category_theory import (
    Object,
    Morphism,
    Identity,
    Functor,
    NaturalTransformation,
    AgentCategory,
    MemoryMonad,
    MaybeMonad,
    YonedaEmbedding,
)


class TestObject:
    def test_create_object(self):
        obj = Object("test")
        assert obj.name == "test"
    
    def test_object_equality(self):
        obj1 = Object("test")
        obj2 = Object("test")
        assert obj1 == obj2
    
    def test_object_inequality(self):
        obj1 = Object("test1")
        obj2 = Object("test2")
        assert obj1 != obj2


class TestMorphism:
    def test_create_morphism(self):
        source = Object("A")
        target = Object("B")
        morph = Morphism(source, target, lambda x: x * 2)
        assert morph.source == source
        assert morph.target == target
    
    def test_apply_morphism(self):
        source = Object("A")
        target = Object("B")
        morph = Morphism(source, target, lambda x: x * 2)
        assert morph(5) == 10
    
    def test_compose_morphisms(self):
        A = Object("A")
        B = Object("B")
        C = Object("C")
        
        f = Morphism(A, B, lambda x: x + 1)
        g = Morphism(B, C, lambda x: x * 2)
        
        composed = f.compose(g)
        assert composed.source == A
        assert composed.target == C
        assert composed(5) == 12  # (5 + 1) * 2
    
    def test_compose_type_mismatch(self):
        A = Object("A")
        B = Object("B")
        C = Object("C")
        
        f = Morphism(A, B, lambda x: x)
        g = Morphism(A, C, lambda x: x)  # Wrong source
        
        with pytest.raises(ValueError, match="Cannot compose"):
            f.compose(g)

    def test_identity_laws_hold_extensionally(self):
        A = Object("A")
        B = Object("B")
        morph = Morphism[int, int](A, B, lambda x: x + 1)

        left_identity = Identity(A).compose(morph)
        right_identity = morph.compose(Identity(B))

        assert left_identity(5) == morph(5)
        assert right_identity(5) == morph(5)

    def test_associativity_holds_extensionally(self):
        A = Object("A")
        B = Object("B")
        C = Object("C")
        D = Object("D")
        f = Morphism[int, int](A, B, lambda value: value + 1)
        g = Morphism[int, int](B, C, lambda value: value * 2)
        h = Morphism[int, int](C, D, lambda value: value - 3)

        left = f.compose(g).compose(h)
        right = f.compose(g.compose(h))

        assert left(5) == right(5)


class TestIdentity:
    def test_identity_morphism(self):
        obj = Object("test")
        id_morph = Identity(obj)
        assert id_morph.source == obj
        assert id_morph.target == obj
    
    def test_identity_applies_to_self(self):
        obj = Object("test")
        id_morph = Identity(obj)
        assert id_morph(42) == 42
        assert id_morph("hello") == "hello"


class TestFunctor:
    def test_functor_map_object(self):
        class SuffixFunctor(Functor):
            def map_object(self, obj):
                return Object(f"{obj.name}_mapped")
            
            def map_morphism(self, morphism):
                return Morphism(
                    self.map_object(morphism.source),
                    self.map_object(morphism.target),
                    morphism.func
                )
        
        F = SuffixFunctor()
        obj = Object("test")
        mapped = F.map_object(obj)
        assert mapped.name == "test_mapped"
    
    def test_functor_map_morphism(self):
        class SuffixFunctor(Functor):
            def map_object(self, obj):
                return Object(f"{obj.name}_mapped")
            
            def map_morphism(self, morphism):
                return Morphism(
                    self.map_object(morphism.source),
                    self.map_object(morphism.target),
                    morphism.func
                )
        
        F = SuffixFunctor()
        A = Object("A")
        B = Object("B")
        morph = Morphism(A, B, lambda x: x + 1)
        
        mapped = F.map_morphism(morph)
        assert mapped(5) == 6

    def test_functor_call_rejects_unknown_values(self):
        class IdentityFunctor(Functor):
            def map_object(self, obj):
                return obj

            def map_morphism(self, morphism):
                return morphism

        with pytest.raises(TypeError, match="Cannot apply functor"):
            IdentityFunctor()(42)

    def test_structure_preserving_functor_laws_extensionally(self):
        class SuffixFunctor(Functor):
            def map_object(self, obj):
                return Object(f"{obj.name}_mapped")

            def map_morphism(self, morphism):
                return Morphism(
                    self.map_object(morphism.source),
                    self.map_object(morphism.target),
                    morphism.func,
                )

        A = Object("A")
        B = Object("B")
        C = Object("C")
        f = Morphism[int, int](A, B, lambda value: value + 1)
        g = Morphism[int, int](B, C, lambda value: value * 2)
        functor = SuffixFunctor()

        mapped_identity = functor.map_morphism(Identity(A))
        mapped_composition = functor.map_morphism(f.compose(g))
        composed_mappings = functor.map_morphism(f).compose(
            functor.map_morphism(g)
        )

        assert mapped_identity(5) == 5
        assert mapped_composition(5) == composed_mappings(5)


class TestNaturalTransformation:
    class RenameFunctor(Functor):
        def __init__(self, suffix):
            self.suffix = suffix

        def map_object(self, obj):
            return Object(f"{obj.name}{self.suffix}")

        def map_morphism(self, morphism):
            return Morphism(
                self.map_object(morphism.source),
                self.map_object(morphism.target),
                morphism.func,
            )

    def test_valid_component(self):
        obj = Object("A")
        source = self.RenameFunctor("_source")
        target = self.RenameFunctor("_target")
        component = Morphism(source.map_object(obj), target.map_object(obj), lambda x: x)

        transformation = NaturalTransformation(
            "rename", source, target, {obj: component}
        )

        assert transformation.component(obj)("value") == "value"

    def test_invalid_component_endpoints_are_rejected(self):
        obj = Object("A")
        source = self.RenameFunctor("_source")
        target = self.RenameFunctor("_target")
        invalid = Morphism(Object("wrong"), target.map_object(obj), lambda x: x)

        with pytest.raises(ValueError, match="Invalid component"):
            NaturalTransformation("rename", source, target, {obj: invalid})


class TestAgentCategory:
    def test_create_category(self):
        cat = AgentCategory("TestCat")
        assert cat.name == "TestCat"
        assert len(cat.objects) == 0
        assert len(cat.morphisms) == 0
    
    def test_add_object(self):
        cat = AgentCategory("TestCat")
        obj = Object("test")
        cat.add_object(obj)
        assert obj in cat.objects

    def test_add_object_is_idempotent(self):
        cat = AgentCategory("TestCat")
        obj = Object("test")

        cat.add_object(obj)
        cat.add_object(obj)

        assert cat.objects == [obj]
    
    def test_add_morphism(self):
        cat = AgentCategory("TestCat")
        A = Object("A")
        B = Object("B")
        morph = Morphism(A, B, lambda x: x)
        cat.add_morphism(morph)
        
        assert morph in cat.morphisms
        assert A in cat.objects
        assert B in cat.objects
    
    def test_identity(self):
        cat = AgentCategory("TestCat")
        obj = Object("test")
        cat.add_object(obj)
        
        id_morph = cat.identity(obj)
        assert id_morph.source == obj
        assert id_morph.target == obj
    
    def test_identity_not_in_category(self):
        cat = AgentCategory("TestCat")
        obj = Object("test")
        
        with pytest.raises(ValueError, match="not in category"):
            cat.identity(obj)
    
    def test_compose_chain(self):
        cat = AgentCategory("TestCat")
        A = Object("A")
        B = Object("B")
        C = Object("C")
        
        f = Morphism(A, B, lambda x: x + 1)
        g = Morphism(B, C, lambda x: x * 2)
        
        chain = cat.compose_chain([f, g])
        assert chain.source == A
        assert chain.target == C
        assert chain(5) == 12
    
    def test_compose_empty_chain(self):
        cat = AgentCategory("TestCat")
        
        with pytest.raises(ValueError, match="Cannot compose empty"):
            cat.compose_chain([])


class TestMemoryMonad:
    def test_unit(self):
        mem = MemoryMonad("initial", [])
        unit = mem.unit(42)
        assert unit.value == 42
        assert unit.memory_state == []
    
    def test_bind(self):
        mem = MemoryMonad(10, [])
        result = mem.bind(lambda x: MemoryMonad(x * 2, [x]))
        assert result.value == 20
        assert result.memory_state == [10]
    
    def test_store(self):
        mem = MemoryMonad("initial", [])
        mem = mem.store("fact1")
        mem = mem.store("fact2")
        assert mem.recall() == ["fact1", "fact2"]
    
    def test_recall(self):
        mem = MemoryMonad("initial", ["a", "b", "c"])
        assert mem.recall() == ["a", "b", "c"]
    
    def test_memory_accumulation(self):
        mem = MemoryMonad(1, [])
        result = mem.bind(lambda x: MemoryMonad(x + 1, [x]))
        result = result.bind(lambda x: MemoryMonad(x + 1, [x]))
        assert result.memory_state == [1, 2]

    def test_right_identity_does_not_duplicate_memory(self):
        mem = MemoryMonad(10, ["existing"])

        assert mem.bind(lambda value: mem.unit(value)) == mem

    def test_left_identity(self):
        unit = MemoryMonad[int](0, [])
        transform = lambda value: MemoryMonad(value + 1, ["transform"])

        assert unit.unit(2).bind(transform) == transform(2)

    def test_associativity(self):
        mem = MemoryMonad(2, ["start"])
        f = lambda value: MemoryMonad(value + 1, ["f"])
        g = lambda value: MemoryMonad(value * 3, ["g"])

        assert mem.bind(f).bind(g) == mem.bind(lambda value: f(value).bind(g))


class TestMaybeMonad:
    def test_just(self):
        just = MaybeMonad(42)
        assert just.is_just()
        assert not just.is_nothing()
    
    def test_nothing(self):
        nothing = MaybeMonad(None)
        assert nothing.is_nothing()
        assert not nothing.is_just()
    
    def test_unit(self):
        mem = MaybeMonad(10)
        unit = mem.unit(42)
        assert unit.value == 42
    
    def test_bind_just(self):
        just = MaybeMonad(10)
        result = just.bind(lambda x: MaybeMonad(x * 2))
        assert result.value == 20
    
    def test_bind_nothing(self):
        nothing = MaybeMonad(None)
        result = nothing.bind(lambda x: MaybeMonad(x * 2))
        assert result.value is None
    
    def test_bind_chain(self):
        just = MaybeMonad(5)
        result = (
            just
            .bind(lambda x: MaybeMonad(x + 1))
            .bind(lambda x: MaybeMonad(x * 2))
        )
        assert result.value == 12


class TestYonedaEmbedding:
    def test_accepts_only_category_morphisms_targeting_object(self):
        category = AgentCategory("TestCat")
        source = Object("A")
        target = Object("B")
        morphism = Morphism(source, target, lambda value: value)
        outsider = Morphism(source, target, lambda value: value)
        category.add_morphism(morphism)

        hom = YonedaEmbedding(category).embed(target)

        assert hom(morphism) is morphism
        assert hom(outsider) is None

    def test_rejects_object_outside_category(self):
        category = AgentCategory("TestCat")

        with pytest.raises(ValueError, match="not in category"):
            YonedaEmbedding(category).embed(Object("outside"))
