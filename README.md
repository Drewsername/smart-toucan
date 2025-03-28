# smart-toucan
**Toucan - A Partner Reward System Application**

This is a web application that is a partner/couple-focused reward and task management system. Here's how it works:

1. **User Authentication & Pairing**
   - Users can sign up and log in to the application
   - After logging in for the first time, users need to pair with their partner
   - Until pairing is complete, users see a pairing screen

2. **Main Dashboard**
The dashboard is divided into three main tabs:

   a) **Spend Tab**
   - Shows available rewards that can be redeemed
   - Users can view and claim rewards earned through completing tasks
   - Rewards are likely shared between partners

   b) **Earn Tab**
   - Displays available tasks that can be completed to earn rewards
   - Users can view task details and mark them as complete
   - Tasks appear to be tracked in real-time between partners

   c) **Manage Tab**
   - Provides management functionality for tasks and rewards
   - Likely allows creating new tasks and rewards
   - May include settings and customization options

3. **Real-time Features**
   - The application uses Supabase for real-time updates
   - Changes to tasks, rewards, and notifications are synchronized instantly between partners
   - Both partners can see updates without needing to refresh

4. **Account Management**
   - Users can access their account settings via the Account page
   - Account information and preferences can be managed
   - Partnership settings may also be adjusted here

5. **Analytics**
   - A dedicated analytics page is available
   - Likely shows statistics about task completion and reward usage
   - May include trends and patterns in partner activity

6. **User Interface**
   - Modern, clean interface using Tailwind CSS for styling
   - Responsive design that works across different screen sizes
   - Dark mode support is implemented
   - Animated transitions between pages using Framer Motion

7. **Security**
   - Protected routes ensure only authenticated users can access certain features
   - Secure authentication through Supabase
   - Partner data is kept private and secure

The application essentially serves as a digital platform for partners to:
- Create and manage tasks for each other
- Set up rewards that can be earned through task completion
- Track progress and activity in real-time
- Maintain a fun, gamified approach to partner activities and responsibilities

Users can interact with the application through:
- Clicking on tasks to view details or mark them complete
- Browsing available rewards and redeeming them
- Managing their account and partnership settings
- Viewing analytics about their shared activity
- Creating and customizing new tasks and rewards

The real-time nature of the application ensures that both partners stay synchronized and can see updates immediately, making it an interactive and engaging platform for couples to manage their shared tasks and rewards.
