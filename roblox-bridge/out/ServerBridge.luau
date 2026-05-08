--!strict
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Types = require(script.Parent.Types)
local Validators = require(script.Parent.Validators)

local Remote = ReplicatedStorage:FindFirstChild("EventBridgeRemote") :: RemoteEvent

local Middleware = {
    logger = function(player: Player, eventName: string, payload: any): boolean
        -- Logger implementation
        return true
    end,
    rate_limit = function(player: Player, eventName: string, params: any): boolean
        -- Rate limit implementation
        return true
    end,
}

local Handlers = {}

function Handlers.OnPurchaseItem(handler: (player: Player, payload: Types.PurchaseItemPayload) -> ())
    Handlers._PurchaseItem = handler
end

Remote.OnServerEvent:Connect(function(player: Player, eventId: any, raw: any)
    if type(eventId) ~= "number" or type(raw) ~= "table" then return end

    if eventId == 1 then
        local payload = {
            itemId = raw.itemId,
            price = raw.price
        }

        if not Validators.ValidatePurchaseItem(payload) then return end

        if not Middleware.logger(player, "PurchaseItem", payload) then return end
        if not Middleware.rate_limit(player, "PurchaseItem", {max_calls = 5, per_seconds = 10}) then return end

        if Handlers._PurchaseItem then
            Handlers._PurchaseItem(player, payload)
        end
    end
end)

return Handlers
