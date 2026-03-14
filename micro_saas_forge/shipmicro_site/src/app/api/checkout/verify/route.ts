import { NextResponse } from "next/server";
import { currentUser, clerkClient } from "@clerk/nextjs/server";

export async function POST(req: Request) {
    try {
        const user = await currentUser();
        if (!user) {
            return new NextResponse("Unauthorized", { status: 401 });
        }

        const body = await req.json();
        const { subscriptionID } = body;

        if (!subscriptionID) {
            return new NextResponse("Missing subscription ID", { status: 400 });
        }

        // Update Clerk User publicMetadata to grant Pro access
        const client = await clerkClient();
        await client.users.updateUserMetadata(user.id, {
            publicMetadata: {
                isPro: true,
                paypalSubscriptionId: subscriptionID,
            }
        });

        return NextResponse.json({ success: true });
    } catch (error) {
        console.error("PayPal verify error:", error);
        return new NextResponse("Internal server error", { status: 500 });
    }
}
