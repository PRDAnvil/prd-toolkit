"""Black-box tests of the plugin's LICENSE, NOTICE and credits (test-cases/release.yaml, FR-275)."""

from release_support import flat, preadme, read_text, section


def test_license_file_and_section():
    """@prd T-275.1"""
    lines = read_text("prd-toolkit/LICENSE").splitlines()
    assert len(lines) == 21
    assert lines[0] == "MIT License"
    assert lines[2] == "Copyright (c) 2026 Ivan Histand"
    text = flat(section(preadme(), "License"))
    for s in ["MIT; see [LICENSE](./LICENSE).", "A vendored `.prd-toolkit/` carries a copy of it."]:
        assert s in text, s


def test_notice():
    """@prd T-275.2"""
    text = flat(read_text("prd-toolkit/NOTICE"))
    for s in [
        "GitHub Spec Kit (https://github.com/github/spec-kit) - MIT License",
        "cc-sdd (https://github.com/gotalab/cc-sdd) - MIT License",
        "BMAD-METHOD (https://github.com/bmad-code-org/BMAD-METHOD) - MIT License",
        "(https://github.com/mattpocock/skills, skills/productivity/grilling) - MIT License",
        "(https://github.com/anthropics/skills, skills/doc-coauthoring) - Apache License 2.0",
        "Nothing is copied from Taskmaster (Commons Clause) or spec-workflow-mcp (GPL-3.0).",
    ]:
        assert s in text, s


def test_credits():
    """@prd T-275.3"""
    text = flat(section(preadme(), "Credits"))
    for s in ["GitHub Spec Kit", "cc-sdd", "BMAD-METHOD", "mattpocock/skills",
              "Anthropic's doc-coauthoring skill", "[NOTICE](./NOTICE)"]:
        assert s in text, s
