// First, define the Comment type
export type Comment = {
  id: number;
  username: string;
  avatar: string;
  comment: string;
  likes: number;
};

// Then update your Post type
export type Post = {
  id: number;
  image: string;
  text: string;
  likes: number;
  comments_nr: number; // total number of comments
  location: string;
  comments: Comment[]; // array of Comment objects
};


export const posts = [
 {
  id: 1,
  text: "Just finished an amazing hike today!",
  image: "https://picsum.photos/id/1018/600/400",
  location: "Yosemite National Park",
  likes: 120,
  comments_nr: 30, // updated total number of comments
  comments: [
    {
      id: 1,
      username: "@jane_smith",
      avatar: "https://randomuser.me/api/portraits/women/45.jpg",
      comment: "Love this post! The photo is amazing aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa 😍",
      likes: 12,
    },
    {
      id: 2,
      username: "@mark_88",
      avatar: "https://randomuser.me/api/portraits/men/32.jpg",
      comment: "Wow, that location looks incredible! 🌄",
      likes: 8,
    },
    {
      id: 3,
      username: "@sarah_lee",
      avatar: "https://randomuser.me/api/portraits/women/68.jpg",
      comment: "I need to try this place soon 😋",
      likes: 5,
    },
    {
      id: 4,
      username: "@alex_tr",
      avatar: "https://randomuser.me/api/portraits/men/75.jpg",
      comment: "Such a vibe! Great capture 📸",
      likes: 10,
    },
    {
      id: 5,
      username: "@lily_rose",
      avatar: "https://randomuser.me/api/portraits/women/12.jpg",
      comment: "This post just made my day 💛",
      likes: 15,
    },
    // Add 25 more comments by slightly modifying usernames or text
    {
      id: 6,
      username: "@hiker_john",
      avatar: "https://randomuser.me/api/portraits/men/45.jpg",
      comment: "Beautiful view! Yosemite never disappoints 🌲",
      likes: 3,
    },
    {
      id: 7,
      username: "@adventure_amy",
      avatar: "https://randomuser.me/api/portraits/women/23.jpg",
      comment: "Adding this to my bucket list 😍",
      likes: 7,
    },
    {
      id: 8,
      username: "@mountain_mike",
      avatar: "https://randomuser.me/api/portraits/men/22.jpg",
      comment: "Looks like the perfect hike! 🥾",
      likes: 5,
    },
    {
      id: 9,
      username: "@nature_lover",
      avatar: "https://randomuser.me/api/portraits/women/12.jpg",
      comment: "The scenery is unreal! 😍",
      likes: 6,
    },
    {
      id: 10,
      username: "@sunset_chaser",
      avatar: "https://randomuser.me/api/portraits/men/30.jpg",
      comment: "I can almost feel the fresh air 🌬️",
      likes: 4,
    },
    {
      id: 11,
      username: "@wanderlust_will",
      avatar: "https://randomuser.me/api/portraits/men/35.jpg",
      comment: "Epic hike! Definitely trying this trail soon 🏞️",
      likes: 8,
    },
    {
      id: 12,
      username: "@explorer_ella",
      avatar: "https://randomuser.me/api/portraits/women/44.jpg",
      comment: "So peaceful, makes me want to visit immediately 🌿",
      likes: 10,
    },
    {
      id: 13,
      username: "@trailblazer_tom",
      avatar: "https://randomuser.me/api/portraits/men/51.jpg",
      comment: "Amazing shot! Love the colors 📸",
      likes: 2,
    },
    {
      id: 14,
      username: "@forest_fiona",
      avatar: "https://randomuser.me/api/portraits/women/60.jpg",
      comment: "Nature at its finest! 😍",
      likes: 5,
    },
    {
      id: 15,
      username: "@adventure_andy",
      avatar: "https://randomuser.me/api/portraits/men/65.jpg",
      comment: "That looks like a challenging trail, love it! 🥾",
      likes: 6,
    },
    {
      id: 16,
      username: "@hiking_hannah",
      avatar: "https://randomuser.me/api/portraits/women/34.jpg",
      comment: "Absolutely stunning view! 😍",
      likes: 8,
    },
    {
      id: 17,
      username: "@mountain_mel",
      avatar: "https://randomuser.me/api/portraits/women/28.jpg",
      comment: "Adding Yosemite to my travel list! 🌲",
      likes: 3,
    },
    {
      id: 18,
      username: "@outdoor_oliver",
      avatar: "https://randomuser.me/api/portraits/men/12.jpg",
      comment: "Wow, the lighting is perfect here! ☀️",
      likes: 7,
    },
    {
      id: 19,
      username: "@peak_peter",
      avatar: "https://randomuser.me/api/portraits/men/19.jpg",
      comment: "Feeling inspired to hike this weekend! 🥾",
      likes: 4,
    },
    {
      id: 20,
      username: "@valley_victoria",
      avatar: "https://randomuser.me/api/portraits/women/15.jpg",
      comment: "Yosemite never gets old 😍",
      likes: 5,
    },
    {
      id: 21,
      username: "@climber_carl",
      avatar: "https://randomuser.me/api/portraits/men/20.jpg",
      comment: "That looks intense but fun! 💪",
      likes: 6,
    },
    {
      id: 22,
      username: "@trail_tina",
      avatar: "https://randomuser.me/api/portraits/women/22.jpg",
      comment: "So peaceful! Can almost hear the birds 🐦",
      likes: 7,
    },
    {
      id: 23,
      username: "@nature_nick",
      avatar: "https://randomuser.me/api/portraits/men/26.jpg",
      comment: "Can’t wait to hike here myself 🌿",
      likes: 8,
    },
    {
      id: 24,
      username: "@sunrise_sam",
      avatar: "https://randomuser.me/api/portraits/men/29.jpg",
      comment: "That sunrise must have been epic! 🌅",
      likes: 5,
    },
    {
      id: 25,
      username: "@forest_faith",
      avatar: "https://randomuser.me/api/portraits/women/38.jpg",
      comment: "Yosemite looks so magical! ✨",
      likes: 6,
    },
    {
      id: 26,
      username: "@explorer_ed",
      avatar: "https://randomuser.me/api/portraits/men/31.jpg",
      comment: "What a view! Definitely on my bucket list 🌄",
      likes: 7,
    },
    {
      id: 27,
      username: "@hiker_hazel",
      avatar: "https://randomuser.me/api/portraits/women/42.jpg",
      comment: "Wow, looks like heaven on earth 😍",
      likes: 8,
    },
    {
      id: 28,
      username: "@adventure_arthur",
      avatar: "https://randomuser.me/api/portraits/men/33.jpg",
      comment: "I love this! So inspiring 🥾",
      likes: 6,
    },
    {
      id: 29,
      username: "@scenic_sophie",
      avatar: "https://randomuser.me/api/portraits/women/36.jpg",
      comment: "Beautiful! Can almost feel the fresh air 🌬️",
      likes: 5,
    },
    {
      id: 30,
      username: "@mountain_maria",
      avatar: "https://randomuser.me/api/portraits/women/40.jpg",
      comment: "This post made my day! Love Yosemite 💛",
      likes: 9,
    },
  ],
},

  {
    id: 2,
    text: "Trying out a new recipe for dinner tonight!",
    image: "https://picsum.photos/id/1025/600/400",
    location: "Home Kitchen",
    likes: 87,
    comments_nr: 3,
    comments: [
      {
        id: 1,
        username: "@chef_mike",
        avatar: "https://randomuser.me/api/portraits/men/22.jpg",
        comment: "Looks delicious! 🍝",
        likes: 7,
      },
      {
        id: 2,
        username: "@foodie_anna",
        avatar: "https://randomuser.me/api/portraits/women/55.jpg",
        comment: "I need that recipe ASAP 😋",
        likes: 9,
      },
      {
        id: 3,
        username: "@cookingwithlove",
        avatar: "https://randomuser.me/api/portraits/women/23.jpg",
        comment: "Yum! Save me some! ❤️",
        likes: 4,
      },
    ],
  },
  {
    id: 3,
    text: "Sunset by the beach. Nothing beats this view.",
    image: "https://picsum.photos/id/1003/600/400",
    location: "Santa Monica",
    likes: 205,
    comments_nr: 4,
    comments: [
      {
        id: 1,
        username: "@beach_bum",
        avatar: "https://randomuser.me/api/portraits/men/11.jpg",
        comment: "Absolutely breathtaking 🌅",
        likes: 18,
      },
      {
        id: 2,
        username: "@sunset_lover",
        avatar: "https://randomuser.me/api/portraits/women/77.jpg",
        comment: "This is my dream sunset! 😍",
        likes: 12,
      },
      {
        id: 3,
        username: "@wave_rider",
        avatar: "https://randomuser.me/api/portraits/men/40.jpg",
        comment: "Perfect spot for reflection 🙌",
        likes: 6,
      },
      {
        id: 4,
        username: "@photog_lily",
        avatar: "https://randomuser.me/api/portraits/women/33.jpg",
        comment: "The colors are insane! 📸",
        likes: 20,
      },
    ],
  },
];
