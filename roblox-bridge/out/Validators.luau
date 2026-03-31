--!strict
local Types = require(script.Parent.Types)

local Validators = {}

function Validators.ValidatePurchaseItem(payload: any): boolean
    if type(payload) ~= "table" then return false end
    if type(payload.itemId) ~= "string" then return false end
    if type(payload.price) ~= "number" then return false end
    return true
end

return Validators
