const fs = require('fs');

function fix(file, typeNames) {
  let content = fs.readFileSync(file, 'utf8');
  content = content.replace(/import type \{[^\}]*\} from ['"]\.\.\/\.\.\/types['"];?/g, 'import type { ' + typeNames + ' } from "../../types";');
  content = content.replace(/import type \{[^\}]*\} from ['"]\.\.\/types['"];?/g, 'import type { ' + typeNames + ' } from "../types";');
  
  content = content.replace(/import \{[^\}]*\} from ['"]\.\.\/\.\.\/types['"];?/g, 'import type { ' + typeNames + ' } from "../../types";');
  content = content.replace(/import \{[^\}]*\} from ['"]\.\.\/types['"];?/g, 'import type { ' + typeNames + ' } from "../types";');

  fs.writeFileSync(file, content);
}

fix('src/components/shared/EvidenceCard.tsx', 'Evidence');
fix('src/components/shared/ExecutionStepItem.tsx', 'ExecutionStep');
fix('src/hooks/usePlanner.ts', 'PlannerEvent, PlannerState');
fix('src/repositories/mock/customer.mock.ts', 'Customer');
fix('src/repositories/mock/dashboard.mock.ts', 'DashboardData');
fix('src/repositories/mock/investigation.mock.ts', 'Investigation');
fix('src/repositories/mock/planner.mock.ts', 'PlannerEvent');
fix('src/repositories/mock/queue.mock.ts', 'QueueItem');
fix('src/services/planner.service.ts', 'PlannerEvent');
