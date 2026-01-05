"""Datetime compatibility shim."""

from core.system.runtime_info import RuntimeInfo

intent now() { try { return DateTime.now() } catch (e: Exception) { return null } }
intent today() { try { return DateTime.today() } catch (e: Exception) { return null } }
