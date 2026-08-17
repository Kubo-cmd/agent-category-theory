"""Tests for agent category theory."""

import pytest
from agent_category_theory import (
    Object,
    Morphism,
    Identity,
    Functor,
    AgentCategory,
    MemoryMonad,
    MaybeMonad,
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
        obj = Object("test")
        mapped = F.map_object(obj)
        assert mapped.name == "test_doubled"
    
    def test_functor_map_morphism(self):
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
        A = Object("A")
        B = Object("B")
        morph = Morphism(A, B, lambda x: x + 1)
        
        mapped = F.map_morphism(morph)
        assert mapped(5) == 12  # (5 + 1) * 2


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
