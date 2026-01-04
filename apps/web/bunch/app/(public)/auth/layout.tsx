export default function AuthLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex w-full flex-1 items-center justify-center p-4">
            {children}
        </div>
    )
}
