import { Component } from "@angular/core";

@Component({
  selector: "app-root",
  template: `
    <div style="text-align: center; padding: 50px;">
      <h1>Hello World!</h1>
      <p>Welcome to your Angular app!</p>
      <p>🎉 Frontend is working perfectly!</p>
    </div>
  `,
  styles: [`
    h1 { 
      color: #28a745; 
      font-size: 48px; 
      margin-bottom: 20px;
    }
    p {
      font-size: 18px;
      color: #666;
    }
  `]
})
export class AppComponent {
  title = "Hello World App";
}
