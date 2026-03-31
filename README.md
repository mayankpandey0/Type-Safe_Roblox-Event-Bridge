# Roblox Type-Safe Event Bridge

A deterministic compiler that converts structured schemas (YAML/JSON) into **type-safe, validated, and optimized Luau networking code** for Roblox.

---

## 🚨 Problem

Roblox networking via RemoteEvents is:

* string-based (magic strings)
* loosely typed
* prone to runtime failures
* vulnerable to malformed/exploit payloads
* inefficient in serialization

This leads to:

* silent bugs
* inconsistent client/server contracts
* no enforcement of data correctness

---

## ✅ Solution

This project introduces a **compiler-driven approach**:

Schemas → Compiler → Generated Luau Code

It enforces:

* type-safe payloads
* runtime validation
* deterministic output
* structured networking contracts

---

## ⚙️ How It Works

### Compiler Pipeline

```
Schemas (YAML/JSON)
        ↓
Global Type Registry
        ↓
Semantic IR (Event Contracts)
        ↓
Compiler Passes
  - Normalize
  - Validate
  - Optimize
        ↓
Luau Emitter
        ↓
Generated Code (Client + Server + Validators)
```

---

## 📦 Features

### Type Safety

* Schema-defined payloads
* Generated Luau types
* Runtime validation layer

### Runtime Validation

* Rejects invalid payloads
* Protects against:

  * wrong types
  * missing fields
  * non-table payloads
  * NaN / ±∞ values

### Deterministic Output

* Same input → identical output (byte-for-byte)
* Stable ordering
* No randomness or timestamps

### Compiler Architecture

* IR-based (not template-based)
* Multi-pass system
* Extensible for future targets (e.g. TypeScript)

---

## 🧠 Example

### Input Schema

```yaml
events:
  - name: TestEvent
    payload:
      player: string
      score: number
```

---

### Generated Type

```lua
export type TestEventPayload = {
    player: string,
    score: number,
}
```

---

### Generated Validator

```lua
local Validators = {}

function Validators.ValidateTestEvent(payload)
    if type(payload) ~= "table" then
        return false
    end

    if type(payload.player) ~= "string" then
        return false
    end

    if type(payload.score) ~= "number"
        or payload.score ~= payload.score
        or payload.score == math.huge
        or payload.score == -math.huge then
        return false
    end

    return true
end

return Validators
```

---

### Generated Server Handler

```lua
if eventName == "TestEvent" then
    if not Validators.ValidateTestEvent(payload) then
        return
    end

    if ServerBridge.OnTestEvent then
        ServerBridge.OnTestEvent(player, payload)
    end
end
```

---

## 🏗️ Project Structure

```
roblox-bridge/
├── core/
│   ├── registry.py
│   ├── compiler.py
│   ├── ir_models.py
│   └── passes/
│       ├── normalize.py
│       ├── validate.py
│       └── optimize.py
│
├── emitters/
│   └── luau_emitter.py
│
├── schemas/
├── out/
├── bridge.py
└── bridge.lock.json
```

---

## 🚀 Usage

### Generate Code

```bash
python bridge.py generate
```

### Output

```
out/
├── ClientBridge.luau
├── ServerBridge.luau
├── Types.luau
└── Validators.luau
```

---

## 🔒 Validation Guarantees

The generated system ensures:

* payload must be a table
* all required fields exist
* strict type checking
* numeric safety:

  * rejects NaN
  * rejects ±∞

---

## 🧪 Testing

Validated using:

* schema → IR → code traceability
* encode/decode bijection checks
* adversarial payload testing
* deterministic output verification

---

## 📈 Roadmap

* tuple encoding (network optimization)
* minified payload keys
* middleware system (rate limiting, logging)
* multi-file schema support
* TypeScript emitter (roblox-ts)

---

## ❌ Non-Goals

* runtime schema inference
* dynamic typing
* AI-based validation
* non-deterministic generation

---

## 🎯 Why This Project Matters

This is a **compiler-grade devtool** demonstrating:

* systems design (compiler architecture)
* type safety in dynamic environments
* secure networking patterns
* deterministic build systems

---

## 📌 Summary

Transforms Roblox networking from:

> loosely typed + error-prone

into:

> deterministic + type-safe + validated system

---

## 📜 License

MIT 
