"""Cross-package subclass discovery driven by the installed package dependency graph.

Provides the machinery for locating subclass implementations across every
installed package that depends on a given root, without requiring explicit
registration. Plugin hierarchies declare their scope once and the package
resolves all implementations automatically across the dependency graph.
"""
