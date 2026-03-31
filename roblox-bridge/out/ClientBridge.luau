--!strict
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Types = require(script.Parent.Types)

local Remote = ReplicatedStorage:WaitForChild("EventBridgeRemote") :: RemoteEvent

local ClientBridge = {}

function ClientBridge.FirePurchaseItem(payload: Types.PurchaseItemPayload)
    local encoded = {
        itemId = payload.itemId,
        price = payload.price
    }
    Remote:FireServer(1, encoded)
end

return ClientBridge
