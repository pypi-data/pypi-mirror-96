// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#include "frc2/command/button/Trigger.h"

#include "frc2/command/InstantCommand.h"

using namespace frc2;

Trigger::Trigger(const Trigger& other) = default;

Trigger Trigger::WhenActive(std::shared_ptr<Command> command, bool interruptible) {
  CommandScheduler::GetInstance().AddButton(
      [pressedLast = m_isActive(), *this, command, interruptible]() mutable {
        bool pressed = m_isActive();

        if (!pressedLast && pressed) {
          command->Schedule(interruptible);
        }

        pressedLast = pressed;
      });

  return *this;
}

Trigger Trigger::WhenActive(std::function<void()> toRun,
                            std::initializer_list<std::shared_ptr<Subsystem>> requirements) {
  return WhenActive(std::move(toRun), wpi::makeArrayRef(requirements.begin(),
                                                        requirements.end()));
}

Trigger Trigger::WhenActive(std::function<void()> toRun,
                            wpi::ArrayRef<std::shared_ptr<Subsystem>> requirements) {
  return WhenActive(InstantCommand(std::move(toRun), requirements));
}

Trigger Trigger::WhileActiveContinous(std::shared_ptr<Command> command, bool interruptible) {
  CommandScheduler::GetInstance().AddButton(
      [pressedLast = m_isActive(), *this, command, interruptible]() mutable {
        bool pressed = m_isActive();

        if (pressed) {
          command->Schedule(interruptible);
        } else if (pressedLast && !pressed) {
          command->Cancel();
        }

        pressedLast = pressed;
      });
  return *this;
}

Trigger Trigger::WhileActiveContinous(
    std::function<void()> toRun,
    std::initializer_list<std::shared_ptr<Subsystem>> requirements) {
  return WhileActiveContinous(
      std::move(toRun),
      wpi::makeArrayRef(requirements.begin(), requirements.end()));
}

Trigger Trigger::WhileActiveContinous(std::function<void()> toRun,
                                      wpi::ArrayRef<std::shared_ptr<Subsystem>> requirements) {
  return WhileActiveContinous(InstantCommand(std::move(toRun), requirements));
}

Trigger Trigger::WhileActiveOnce(std::shared_ptr<Command> command, bool interruptible) {
  CommandScheduler::GetInstance().AddButton(
      [pressedLast = m_isActive(), *this, command, interruptible]() mutable {
        bool pressed = m_isActive();

        if (!pressedLast && pressed) {
          command->Schedule(interruptible);
        } else if (pressedLast && !pressed) {
          command->Cancel();
        }

        pressedLast = pressed;
      });
  return *this;
}

Trigger Trigger::WhenInactive(std::shared_ptr<Command> command, bool interruptible) {
  CommandScheduler::GetInstance().AddButton(
      [pressedLast = m_isActive(), *this, command, interruptible]() mutable {
        bool pressed = m_isActive();

        if (pressedLast && !pressed) {
          command->Schedule(interruptible);
        }

        pressedLast = pressed;
      });
  return *this;
}

Trigger Trigger::WhenInactive(std::function<void()> toRun,
                              std::initializer_list<std::shared_ptr<Subsystem>> requirements) {
  return WhenInactive(std::move(toRun), wpi::makeArrayRef(requirements.begin(),
                                                          requirements.end()));
}

Trigger Trigger::WhenInactive(std::function<void()> toRun,
                              wpi::ArrayRef<std::shared_ptr<Subsystem>> requirements) {
  return WhenInactive(InstantCommand(std::move(toRun), requirements));
}

Trigger Trigger::ToggleWhenActive(std::shared_ptr<Command> command, bool interruptible) {
  CommandScheduler::GetInstance().AddButton(
      [pressedLast = m_isActive(), *this, command, interruptible]() mutable {
        bool pressed = m_isActive();

        if (!pressedLast && pressed) {
          if (command->IsScheduled()) {
            command->Cancel();
          } else {
            command->Schedule(interruptible);
          }
        }

        pressedLast = pressed;
      });
  return *this;
}

Trigger Trigger::CancelWhenActive(std::shared_ptr<Command> command) {
  CommandScheduler::GetInstance().AddButton(
      [pressedLast = m_isActive(), *this, command]() mutable {
        bool pressed = m_isActive();

        if (!pressedLast && pressed) {
          command->Cancel();
        }

        pressedLast = pressed;
      });
  return *this;
}
