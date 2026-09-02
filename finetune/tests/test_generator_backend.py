import pytest
from finetune.datagen.generator_backend import TemplateBackend, get_backend


def test_template_backend_passthrough():
    """Test that TemplateBackend returns user text unchanged when no %%RENDER%% marker"""
    backend = TemplateBackend()
    system = "System prompt"
    user = "Hello world"
    result = backend.complete(system, user)
    assert result == user


def test_template_backend_proforma_style():
    """Test that TemplateBackend properly renders facts in proforma style"""
    backend = TemplateBackend()
    system = "System prompt"
    user = "Patient: John Smith\n%%RENDER%%\n{\"facts\": {\"Diagnosis\": \"Hypertension\", \"Medication\": \"Lisinopril\"}, \"style\": \"proforma\"}"
    result = backend.complete(system, user)
    
    # Should contain each fact in a separate headed line
    assert "Diagnosis: Hypertension" in result
    assert "Medication: Lisinopril" in result
    assert "\n" in result  # Should have newlines


def test_template_backend_prose_style():
    """Test that TemplateBackend properly renders facts in prose style"""
    backend = TemplateBackend()
    system = "System prompt"
    user = "Patient: John Smith\n%%RENDER%%\n{\"facts\": {\"Diagnosis\": \"Hypertension\", \"Medication\": \"Lisinopril\"}, \"style\": \"prose\"}"
    result = backend.complete(system, user)
    
    # Should be a single paragraph without blank lines
    assert "Diagnosis: Hypertension" in result
    assert "Medication: Lisinopril" in result
    assert "\n" not in result  # No newlines between facts


def test_template_backend_deterministic():
    """Test that TemplateBackend is deterministic - same input gives same output"""
    backend = TemplateBackend()
    system = "System prompt"
    
    # Two identical calls should give identical results
    user1 = "Patient: John Smith\n%%RENDER%%\n{\"facts\": {\"Diagnosis\": \"Hypertension\"}, \"style\": \"prose\"}"
    user2 = "Patient: John Smith\n%%RENDER%%\n{\"facts\": {\"Diagnosis\": \"Hypertension\"}, \"style\": \"prose\"}"
    
    result1 = backend.complete(system, user1)
    result2 = backend.complete(system, user2)
    
    assert result1 == result2


def test_get_backend_template():
    """Test that get_backend returns TemplateBackend for 'template'"""
    backend = get_backend("template")
    assert isinstance(backend, TemplateBackend)


def test_get_backend_invalid():
    """Test that get_backend raises ValueError for invalid backend name"""
    with pytest.raises(ValueError):
        get_backend("nope")


def test_get_backend_ollama_not_implemented():
    """Test that get_backend with 'ollama' raises NotImplementedError"""
    backend = get_backend("ollama", model="test")
    with pytest.raises(NotImplementedError):
        backend.complete("system", "user")